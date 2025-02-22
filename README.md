# DokuVimKi

DokuVimKi is a [Vim](https://www.vim.org/) plugin which allows you to edit
[DokuWiki](https://dokuwiki.org) pages via DokuWikis
[XML-RPC](https://dokuwiki.org/devel:xmlrpc) interface. It also does syntax
highlighting for DokuWiki syntax.

## Installation

The recommended way to install DokuVimKi is via a Vim plugin manager like
[`vim-plug`](https://github.com/junegunn/vim-plug) or
[`pathogen.vim`](https://github.com/tpope/vim-pathogen).

For `vim-plug`, add the following to the vim-plug section of your `~/.vimrc`,
which enables the DokuVimKi plugin only when first connecting to a DokuWiki:

```vim
Plug 'kynan/dokuvimki', {'on': 'DokuVimKi'}
```

For `pathogen.vim`, simply run the following:

```bash
cd ~/.vim/bundle
git clone git://github.com/kynan/dokuvimki
```

Alternatively, download the plugin and unpack it in your `~/.vim/` folder.

Note that if you have any other manually installed plugins, you need to merge
the DokuVimKi documentation tags into your existing `doc/tags` file in your
`~/.vim` directory, e.g. by running

```bash
cat dokuvimki/doc/tags >> .vim/doc/tags
```

## Prerequisites

vim needs to be compiled with [python
support](http://vimdoc.sourceforge.net/htmldoc/if_pyth.html), which should be
the case for most distributions e.g. `vim-gnome` or `vim-gtk` on Debian/Ubuntu.

The [`dokuwikixmlrpc`](https://pypi.org/project/dokuwikixmlrpc) python module
needs to be installed. Install it with:

```bash
pip install dokuwikixmlrpc
```

Note that vim will use the Python interpreter it was built with (if you haven't
built vim yourself this will be your system Python) and you will need to install
it for that interpreter. If you'd like to use a virtualenv you need a vim plugin
like [`virtualenv.vim`](https://github.com/plytophogy/vim-virtualenv).

You'll also have to install a recent development version of
[DokuWiki](https://dokuwiki.org) itself in order to use this plugin! For
details on how to setup XMLRPC for DokuWiki please refer to
[config:xmlrpc](https://dokuwiki.org/devel:xmlrpc).

If you want to enable syntax highlighting without issuing `:set
syntax=dokuwiki` when editing pages of a local wiki just put this in your
`~/.vimrc` to make VIM auto-detect DokuWiki files (this is not required for
editing remote wikis via `DWedit`):

```vim
" looks for DokuWiki headlines in the first 20 lines
" of the current buffer
fun IsDokuWiki()
  if match(getline(1,20),'^ \=\(=\{2,6}\).\+\1 *$') >= 0
    set textwidth=0
    set wrap
    set linebreak
    set filetype=dokuwiki
  endif
endfun

" check for dokuwiki syntax
autocmd BufWinEnter *.txt call IsDokuWiki()

syntax on
```

## Configuration

To configure the plugin just add the following to your `~/.vimrc` and change
the values to your needs.

```vim
" user name with which you want to login at the remote wiki
let g:DokuVimKi_USER = 'username'

" password
let g:DokuVimKi_PASS = 'password'

" url of the remote wiki (without trailing '/')
let g:DokuVimKi_URL  = 'https://yourwikidomain.org'

" use HTTP basic auth (optional, defaults to off)
" setting this to any value other than empty string enables the setting
let g:DokuVimKi_HTTP_BASIC_AUTH = 1

" width of the index window (optional, defaults to 30)
let g:DokuVimKi_INDEX_WINWIDTH = 40

" set a default summary for :w (optional, defaults to [xmlrpc dokuvimki edit])
let g:DokuVimKi_DEFAULT_SUM = 'fancy default summary'
```

Once you are set and done you can launch DokuVimKi:

```vim
:DokuVimKi
```

## Highlight groups

The DokuVimKi syntax highligher uses the following highlight groups, which
can be customized:

* DokuBlockColor
* DokuBold
* DokuCode
* DokuCodeMatch
* DokuDel
* DokuFile
* DokuFileMatch
* DokuFootnoteMatch
* DokuFormatColor
* DokuHeadline
* DokuImageMode
* DokuItalic
* DokuLink
* DokuLinkExternal
* DokuLinkInterwiki
* DokuLinkMail
* DokuLinkTitle
* DokuList
* DokuMedia
* DokuMonospaced
* DokuNewLine
* DokuNoWiki
* DokuNoWiki
* DokuQuote
* DokuRule
* DokuSmileys
* DokuSub
* DokuSup
* DokuTableTD
* DokuTableTH
* DokuUnderlined

To override a highlight group, add the following to your `vimrc`:

```vim
hi <group name> <key>=<val> [<key>=<val> ...]
```

See `:help highlight` for further details.

## Commands

For a detailed list of available commands please consult the dokuvimki help:

```vim
:help dokuvimki-commands
```

## Tips

### Shell aliases

To speed up the editing you could add some aliases to your `$SHELLrc`:

```bash
alias vidoku='viDokuVimKi() { vim +DokuVimKi +"DWedit $1" }; viDokuVimKi'
alias gvidoku='gviDokuVimKi() { gvim +DokuVimKi +"DWedit $1" }; gviDokuVimKi'
```

Usage example:

```bash
vidoku playground:DokuVimKi
```

This will create a DokuVimKi document within the playground namespace.

### Outsource DokuVimKi Configuration

A good idea is to outsource your DokuVimKi configuration. To do so, store your
settings in a seperate file like `~/.vim/dokuvimkirc`. You can increase
security be setting the file permission properly

```bash
chmod 600 ~/.vim/dokuvimkirc
```

To include this file in your `~/.vimrc` use following code:

```vim
" Include DokuVimKi Configuration
if filereadable($HOME."/.vim/dokuvimkirc")
  source $HOME/.vim/dokuvimkirc
endif
```

### Create separate aliases for different dokuwikis

One way of keeping your `.vimrc` lean and mean is to avoid loading dokuvimki
specific configuration file unless you want to edit the wiki, while retaining
all your other `.vimrc` magic. To do this simply create a separate
configuration directory called `~/.dokuwiki` which should contain
`mywiki.vim`:

```vim
source ~/.dokuwiki/macros_dokuvimki.vim
let g:DokuVimKi_USER = 'mywikiuser'
let g:DokuVimKi_PASS = 'mywikipassword'
let g:DokuVimKi_URL  = 'http://mywiki.org'
source ~/.dokuwiki/dokuvimki.vim
```

The last bit displays the list of wiki pages by default. Then you are free to
define a custom `macros_dokuvimki.vim` that applies to all your dokuwiki vim
bindings:

```vim
" ensures you retain your normal .vimrc magic
source ~/.vimrc
" remap save commands for convenience
nmap <S-z><S-z> :DWsave<CR>

" looks for DokuWiki headlines in the first 20 lines
" of the current buffer
fun IsDokuWiki()
   if match(getline(1,20),'^ \=\(=\{2,6}\).\+\1 *$') >= 0
      set textwidth=0
      set wrap
      set linebreak
      set filetype=dokuwiki
   endif
endfun

" check for dokuwiki syntax
autocmd BufWinEnter *.txt call IsDokuWiki()

"Authentication has been moved to "~/.dokuwiki/mywiki.vim" specific files

" optional Cursorline, I feel makes editing a bit easier on the eye
"highlight CursorLine guibg=lightgreen cterm=bold ctermbg=17
```

### Invoking dokuvimki via shell alias

Set a distinct alias in your bash shell (usually your `~/.bashrc` file) to
edit *mywiki* using dokuvimki:

```bash
alias vidmywiki='vi -u ~/.dokuwiki/mywiki.vim
```

Now all you need to do on your bash shell prompt is issue:

```bash
vidmywiki
```

and you'll be automatically authenticated into mywiki while retaining all
dokuvimki specific settings within `macros_dokuvim.vim` for sharing amongst
all your dokuwikis. All you have to do is copy the contents of `mywiki.vim` to
`mywiki2.vim`, edit the credentials and create a matching new alias for
`mywiki2.vim` invocation.

## Changelog

* [fixed whitespace check](http://github.com/chimeric/dokuvimki/commit/f368b9c3ba506b128efddaecefa94d7cd3008a5c)
* [disable DokuVimKi command after initialization](http://github.com/chimeric/dokuvimki/commit/6f5413746aef603a088a9ef457d7ca79196c5619)
* [only allow valid pagenames](http://github.com/chimeric/dokuvimki/commit/da4f0d1797f96e066549fb842aa71d6978f78b8a)
* [fixed docs for DWsave](http://github.com/chimeric/dokuvimki/commit/4cce90344c0e2e002fb4a9ee6d4a263c4629a0ac)
* [use error message on dwquit when unsaved changes](http://github.com/chimeric/dokuvimki/commit/c74c1a73818d894f2920167cc89dea9dd8c52315)
* [catch saving of empty new pages](http://github.com/chimeric/dokuvimki/commit/172ec30ddc59e2e28b3b8c0d91fa3420ec309b6f)
* [tracking unsaved pages for all scenarios](http://github.com/chimeric/dokuvimki/commit/72be8cbbd1595528a6826855112a24efa5c8c25a)
* [let the user know if some buffers contain unsaved changes on quit](http://github.com/chimeric/dokuvimki/commit/264af4ed9440f550c121422ead496e538ba241e8)
* [fixed changes tracking](http://github.com/chimeric/dokuvimki/commit/7c42aa80892d6e60179836912331c1d6b12dea4e)
* [cosmetical changes](http://github.com/chimeric/dokuvimki/commit/6ff2d01fc1ab8d62728e706cf7ef1c197096f3d6)
