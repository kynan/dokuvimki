"-----------------------------------------------------------------------------
" Copyright (C) 2010 Michael Klier <chi@chimeric.de>
"
" Permission is hereby granted, free of charge, to any person obtaining
" a copy of this software and associated documentation files (the
" "Software"), to deal in the Software without restriction, including
" without limitation the rights to use, copy, modify, merge, publish,
" distribute, sublicense, and/or sell copies of the Software, and to
" permit persons to whom the Software is furnished to do so, subject to
" the following conditions:

" The above copyright notice and this permission notice shall be
" included in all copies or substantial portions of the Software.

" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
" EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
" MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
" NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
" LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
" OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
" WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"
" Maintainer:   Florian Rathgeber <florian.rathgeber@gmail.com>
"-----------------------------------------------------------------------------

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

if has('python3')
  command! -nargs=1 Py py3 <args>
  command! -nargs=1 Pyfile py3file <args>
elseif has('python')
  command! -nargs=1 Py py <args>
  command! -nargs=1 Pyfile pyfile <args>
endif

if (has('python3') || has('python')) && version > 700
  command! -nargs=0 DokuVimKi exec('Py dokuvimki = DokuVimKi()')

  if !exists('g:DokuVimKi_INDEX_WINWIDTH')
    let g:DokuVimKi_INDEX_WINWIDTH=30
  endif

  if !exists('g:DokuVimKi_DEFAULT_SUM')
    let g:DokuVimKi_DEFAULT_SUM = '[xmlrpc dokuvimki edit]'
  endif

  " Custom autocompletion function for wiki pages and media files
  " the global g:pages g:media variables are set/refreshed
  " when the index is loaded
  fun! InsertModeComplete(findstart, base)
    if a:findstart
      " locate the start of the page/media link
      let line = getline('.')
      let start = col('.') - 1
      while start > 0 && line[start - 1] !~ '\([\|{\)'
        let start -= 1
      endwhile
      if line[start - 1] =~ "["
        let g:comp = "pages"
      elseif line[start - 1] =~ "{"
        let g:comp = "media"
      endif
      return start
    else
      " find matching pages/media
      let res = []
      if g:comp =~ "pages"
        for m in split(g:pages)
          if m =~ '^' . a:base
            call add(res, m)
          endif
        endfor
      elseif g:comp =~ "media"
        for m in split(g:media)
          if m =~ '^' . a:base
            call add(res, m)
          endif
        endfor
      endif
      return res
    endif
  endfun

  " Custom autocompletion function for namespaces and pages in
  " normal mode. Used with DWedit
  fun! CmdModeComplete(ArgLead, CmdLine, CursorPos)
    let res = []
    for m in split(g:pages)
      if m =~ '^' . a:ArgLead
        call add(res, m)
      endif
    endfor
    return res
  endfun

  " Inserts a headline
  let g:headlines = ["======  ======", "=====  =====", "====  ====", "===  ===", "==  =="]
  fun! Headline()
    return g:headlines[g:lvl]
  endfun

  " Sets indentation/headline level
  let g:lvl = 0
  fun! SetLvl(lvl)
    let nlvl = g:lvl + a:lvl
    if nlvl >= 1 && nlvl <= 4
      let g:lvl = nlvl
    endif
    return ''
  endfun

  exe "Pyfile " . escape(s:plugin_path, ' ') . "/dokuvimki.py"
else
  command! -nargs=0 DokuVimKi echoerr "DokuVimKi disabled! Python support missing or vim version not supported."
endif
" vim:ts=4:sw=4:et:
