" DokuWiki Vim Syntaxfile
" Language:      DokuWiki Pages (http://wiki.splitbrain.org/wiki:dokuwiki)
" Maintainer:    Michael Klier <chi@chimeric.de>
" URL:           http://www.chimeric.de/projects/dokuwiki/dokuvimki

if !exists("main_syntax")
  if version < 600
    syntax clear
  elseif exists("b:current_syntax")
    finish
  endif
  let main_syntax = "dokuwiki"
endif

syn case ignore
syn spell toplevel
syn sync linebreaks=1

syn match DokuHeadline          #^ \=\(=\{2,6}\)\(=\)\@!.\+\1 *$#
syn match DokuRule              #^ \=-\{4,} *$#
syn match DokuMonospaced        #''[^'[\]]\+''#
syn match DokuNewLine           #\\\\\( \{1,}\|$\)#
syn match DokuSmileys           #8-)\|8-O\|:-(\|:-)\|=)\|:-/\|:-\\\|:-?\|:-D\|:-P\|:-O\|:-X\|:-|\|;-)\|:?:\|:!:\|\^_\^\|LOL\|FIXME\|DELETEME#
syn match DokuList              #^\( \{2}\| \{4}\| \{6}\| \{8}\| \{10}\| \{12}\| \{14}\| \{16}\| \{18}\| \{20}\| \{22}\| \{24}\)\(\-\|\*\)# 
syn match DokuNoWiki            #%%[^%]\+%%#
syn match DokuQuote             #^>\+#
syn match DokuLinkInterwiki     #[a-z]\+># contained
syn match DokuLinkExternal      #\(http\|https\)\=\(://\)\=\(www\.\)\(\a\|-\)\+\(\.\{1}\l\{2,3}\)\=[^| \]]*#
syn match DokuLinkMail          #<[^@]\+@[^>]\+>#
syn match DokuLinkTitle         #|\zs[^|\]{}]\+# contained
syn match DokuImageMode         #?[^}]\+# contained
syn match DokuTableTH           #\^# contained
syn match DokuTableTD           #|# contained

syn region DokuLink             start=#\[\[# end=#\]\]# contains=DokuLinkInterwiki,DokuLinkExternal,DokuLinkTitle,DokuMedia oneline
syn region DokuMedia            start=#{{#   end=#}}# contains=DokuLinkExternal,DokuImageMode,DokuLinkTitle oneline

syn region DokuSub              start=#<sub># end=#</sub># keepend
syn region DokuSup              start=#<sup># end=#</sup># keepend 
syn region DokuDel              start=#<del># end=#</del># keepend 
syn region DokuFootnote         matchgroup=DokuFootnoteMatch start=#((# end=#))# contains=DokuLink,DokuLinkInterwiki,DokuLinkExternal,DokuLinkTitle,DokuMedia,DokuBold,DokuMonospaced,DokuItalic,DokuUnderlined,DokuSmileys,DokuSub,DokuSup,DokuDel keepend

syn region DokuFileGeneric matchgroup=DokuFileMatch start=#<file.*># end=#</file># keepend
syn region DokuCodeGeneric matchgroup=DokuCodeMatch start=#<code.*># end=#</code># keepend

syn region DokuBold             start=#\*\*# end=#\*\*# contains=DokuItalic,DokuUnderlined,DokuLink oneline
syn region DokuItalic           start=#//# end=#//# skip=#://# contains=DokuBold,DokuUnderlined,DokuLink oneline
syn region DokuUnderlined       start=#__# end=#__# contains=DokuBold,DokuItalic,DokuLink oneline
syn region DokuTableTH          start=#\^# end=#\^\|# contains=DokuTableTH,DokuLink,DokuMedia,DokuBold,DokuItalic,DokuUnderlined,DokuMonospaced,DokuSmileys,DokuNewLine oneline
syn region DokuTableTD          start=#|#  end=#|\|# contains=DokuTableTD,DokuLink,DokuMedia,DokuBold,DokuItalic,DokuUnderlined,DokuMonospaced,DokuSmileys,DokuNewLine oneline

"syn include @abap syntax/abap.vim
"syn region Dokuabap matchgroup=DokuCodeMatch start=#<code abap.*># end=#</code># contains=@abap
"syn include @ada syntax/ada.vim
"syn region Dokuada matchgroup=DokuCodeMatch start=#<code ada.*># end=#</code># contains=@ada
"syn include @apache syntax/apache.vim
"syn region Dokuapache matchgroup=DokuCodeMatch start=#<code apache.*># end=#</code># contains=@apache
"syn include @asm syntax/asm.vim
"syn region Dokuasm matchgroup=DokuCodeMatch start=#<code asm.*># end=#</code># contains=@asm
"syn include @autohotkey syntax/autohotkey.vim
"syn region Dokuautohotkey matchgroup=DokuCodeMatch start=#<code autohotkey.*># end=#</code># contains=@autohotkey
"syn include @autoit syntax/autoit.vim
"syn region Dokuautoit matchgroup=DokuCodeMatch start=#<code autoit.*># end=#</code># contains=@autoit
"syn include @awk syntax/awk.vim
"syn region Dokuawk matchgroup=DokuCodeMatch start=#<code awk.*># end=#</code># contains=@awk
"syn include @cmake syntax/cmake.vim
"syn region Dokucmake matchgroup=DokuCodeMatch start=#<code cmake.*># end=#</code># contains=@cmake
"syn include @cobol syntax/cobol.vim
"syn region Dokucobol matchgroup=DokuCodeMatch start=#<code cobol.*># end=#</code># contains=@cobol
"syn include @c syntax/c.vim
"syn region Dokuc matchgroup=DokuCodeMatch start=#<code c.*># end=#</code># contains=@c
"syn include @cpp syntax/cpp.vim
"syn region Dokucpp matchgroup=DokuCodeMatch start=#<code cpp.*># end=#</code># contains=@cpp
"syn include @css syntax/css.vim
"syn region Dokucss matchgroup=DokuCodeMatch start=#<code css.*># end=#</code># contains=@css
"syn include @diff syntax/diff.vim
"syn region Dokudiff matchgroup=DokuCodeMatch start=#<code diff.*># end=#</code># contains=@diff
"syn include @dot syntax/dot.vim
"syn region Dokudot matchgroup=DokuCodeMatch start=#<code dot.*># end=#</code># contains=@dot
"syn include @d syntax/d.vim
"syn region Dokud matchgroup=DokuCodeMatch start=#<code d.*># end=#</code># contains=@d
"syn include @eiffel syntax/eiffel.vim
"syn region Dokueiffel matchgroup=DokuCodeMatch start=#<code eiffel.*># end=#</code># contains=@eiffel
"syn include @erlang syntax/erlang.vim
"syn region Dokuerlang matchgroup=DokuCodeMatch start=#<code erlang.*># end=#</code># contains=@erlang
"syn include @fortran syntax/fortran.vim
"syn region Dokufortran matchgroup=DokuCodeMatch start=#<code fortran.*># end=#</code># contains=@fortran
"syn include @freebasic syntax/freebasic.vim
"syn region Dokufreebasic matchgroup=DokuCodeMatch start=#<code freebasic.*># end=#</code># contains=@freebasic
"syn include @gdb syntax/gdb.vim
"syn region Dokugdb matchgroup=DokuCodeMatch start=#<code gdb.*># end=#</code># contains=@gdb
"syn include @gnuplot syntax/gnuplot.vim
"syn region Dokugnuplot matchgroup=DokuCodeMatch start=#<code gnuplot.*># end=#</code># contains=@gnuplot
"syn include @groovy syntax/groovy.vim
"syn region Dokugroovy matchgroup=DokuCodeMatch start=#<code groovy.*># end=#</code># contains=@groovy
"syn include @haskell syntax/haskell.vim
"syn region Dokuhaskell matchgroup=DokuCodeMatch start=#<code haskell.*># end=#</code># contains=@haskell
"syn include @idl syntax/idl.vim
"syn region Dokuidl matchgroup=DokuCodeMatch start=#<code idl.*># end=#</code># contains=@idl
"syn include @java syntax/java.vim
"syn region Dokujava matchgroup=DokuCodeMatch start=#<code java.*># end=#</code># contains=@java
"syn include @javascript syntax/javascript.vim
"syn region Dokujavascript matchgroup=DokuCodeMatch start=#<code javascript.*># end=#</code># contains=@javascript
"syn include @lisp syntax/lisp.vim
"syn region Dokulisp matchgroup=DokuCodeMatch start=#<code lisp.*># end=#</code># contains=@lisp
"syn include @logtalk syntax/logtalk.vim
"syn region Dokulogtalk matchgroup=DokuCodeMatch start=#<code logtalk.*># end=#</code># contains=@logtalk
"syn include @lscript syntax/lscript.vim
"syn region Dokulscript matchgroup=DokuCodeMatch start=#<code lscript.*># end=#</code># contains=@lscript
"syn include @lua syntax/lua.vim
"syn region Dokulua matchgroup=DokuCodeMatch start=#<code lua.*># end=#</code># contains=@lua
"syn include @make syntax/make.vim
"syn region Dokumake matchgroup=DokuCodeMatch start=#<code make.*># end=#</code># contains=@make
"syn include @matlab syntax/matlab.vim
"syn region Dokumatlab matchgroup=DokuCodeMatch start=#<code matlab.*># end=#</code># contains=@matlab
"syn include @mmix syntax/mmix.vim
"syn region Dokummix matchgroup=DokuCodeMatch start=#<code mmix.*># end=#</code># contains=@mmix
"syn include @modula3 syntax/modula3.vim
"syn region Dokumodula3 matchgroup=DokuCodeMatch start=#<code modula3.*># end=#</code># contains=@modula3
"syn include @mysql syntax/mysql.vim
"syn region Dokumysql matchgroup=DokuCodeMatch start=#<code mysql.*># end=#</code># contains=@mysql
"syn include @nsis syntax/nsis.vim
"syn region Dokunsis matchgroup=DokuCodeMatch start=#<code nsis.*># end=#</code># contains=@nsis
"syn include @objc syntax/objc.vim
"syn region Dokuobjc matchgroup=DokuCodeMatch start=#<code objc.*># end=#</code># contains=@objc
"syn include @ocaml syntax/ocaml.vim
"syn region Dokuocaml matchgroup=DokuCodeMatch start=#<code ocaml.*># end=#</code># contains=@ocaml
"syn include @pascal syntax/pascal.vim
"syn region Dokupascal matchgroup=DokuCodeMatch start=#<code pascal.*># end=#</code># contains=@pascal
"syn include @perl syntax/perl.vim
"syn region Dokuperl matchgroup=DokuCodeMatch start=#<code perl.*># end=#</code># contains=@perl
"syn include @php syntax/php.vim
"syn region Dokuphp matchgroup=DokuCodeMatch start=#<code php.*># end=#</code># contains=@php
"syn include @pike syntax/pike.vim
"syn region Dokupike matchgroup=DokuCodeMatch start=#<code pike.*># end=#</code># contains=@pike
"syn include @plsql syntax/plsql.vim
"syn region Dokuplsql matchgroup=DokuCodeMatch start=#<code plsql.*># end=#</code># contains=@plsql
"syn include @progress syntax/progress.vim
"syn region Dokuprogress matchgroup=DokuCodeMatch start=#<code progress.*># end=#</code># contains=@progress
"syn include @prolog syntax/prolog.vim
"syn region Dokuprolog matchgroup=DokuCodeMatch start=#<code prolog.*># end=#</code># contains=@prolog
"syn include @python syntax/python.vim
"syn region Dokupython matchgroup=DokuCodeMatch start=#<code python.*># end=#</code># contains=@python
"syn include @rebol syntax/rebol.vim
"syn region Dokurebol matchgroup=DokuCodeMatch start=#<code rebol.*># end=#</code># contains=@rebol
"syn include @robots syntax/robots.vim
"syn region Dokurobots matchgroup=DokuCodeMatch start=#<code robots.*># end=#</code># contains=@robots
"syn include @ruby syntax/ruby.vim
"syn region Dokuruby matchgroup=DokuCodeMatch start=#<code ruby.*># end=#</code># contains=@ruby
"syn include @sas syntax/sas.vim
"syn region Dokusas matchgroup=DokuCodeMatch start=#<code sas.*># end=#</code># contains=@sas
"syn include @scheme syntax/scheme.vim
"syn region Dokuscheme matchgroup=DokuCodeMatch start=#<code scheme.*># end=#</code># contains=@scheme
"syn include @scilab syntax/scilab.vim
"syn region Dokuscilab matchgroup=DokuCodeMatch start=#<code scilab.*># end=#</code># contains=@scilab
"syn include @smarty syntax/smarty.vim
"syn region Dokusmarty matchgroup=DokuCodeMatch start=#<code smarty.*># end=#</code># contains=@smarty
"syn include @sql syntax/sql.vim
"syn region Dokusql matchgroup=DokuCodeMatch start=#<code sql.*># end=#</code># contains=@sql
"syn include @tcl syntax/tcl.vim
"syn region Dokutcl matchgroup=DokuCodeMatch start=#<code tcl.*># end=#</code># contains=@tcl
"syn include @vb syntax/vb.vim
"syn region Dokuvb matchgroup=DokuCodeMatch start=#<code vb.*># end=#</code># contains=@vb
"syn include @verilog syntax/verilog.vim
"syn region Dokuverilog matchgroup=DokuCodeMatch start=#<code verilog.*># end=#</code># contains=@verilog
"syn include @vhdl syntax/vhdl.vim
"syn region Dokuvhdl matchgroup=DokuCodeMatch start=#<code vhdl.*># end=#</code># contains=@vhdl
"syn include @vim syntax/vim.vim
"syn region Dokuvim matchgroup=DokuCodeMatch start=#<code vim.*># end=#</code># contains=@vim
"syn include @whitespace syntax/whitespace.vim
"syn region Dokuwhitespace matchgroup=DokuCodeMatch start=#<code whitespace.*># end=#</code># contains=@whitespace
"syn include @winbatch syntax/winbatch.vim
"syn region Dokuwinbatch matchgroup=DokuCodeMatch start=#<code winbatch.*># end=#</code># contains=@winbatch
"syn include @xml syntax/xml.vim
"syn region Dokuxml matchgroup=DokuCodeMatch start=#<code xml.*># end=#</code># contains=@xml

" costum color groups
hi DokuHeadline           term=bold,underline cterm=bold,underline gui=bold,underline
hi DokuNewLine            term=bold cterm=bold ctermfg=Red gui=bold guifg=Red
hi DokuRule               term=bold cterm=bold ctermfg=Red gui=bold guifg=Red
hi DokuQuote              term=bold cterm=bold ctermfg=Red gui=bold guifg=Red
hi DokuLink               term=bold cterm=bold ctermfg=Green gui=bold guifg=Green
hi DokuMedia              term=bold cterm=bold ctermfg=Yellow gui=bold guifg=Darkyellow
hi DokuLinkInterwiki      term=bold cterm=bold ctermfg=Red gui=bold guifg=Red
hi DokuImageMode          term=bold cterm=bold ctermfg=Red gui=bold guifg=Red
hi DokuLinkExternal       term=bold cterm=bold ctermfg=Magenta gui=bold guifg=Magenta
hi DokuLinkMail           term=bold cterm=bold ctermfg=Magenta gui=bold guifg=Magenta
hi DokuLinkTitle          term=bold cterm=bold ctermfg=Blue gui=bold guifg=Blue
hi DokuSmileys            term=bold ctermbg=Yellow ctermfg=Black guibg=Yellow guifg=Black
hi DokuItalic             term=italic cterm=italic gui=italic
hi DokuBold               term=bold cterm=bold gui=bold
hi DokuUnderlined         term=underline cterm=underline gui=underline
hi DokuSub                term=bold ctermbg=LightBlue ctermfg=Black guibg=LightBlue guifg=Black
hi DokuSup                term=bold ctermbg=LightBlue ctermfg=Black guibg=LightBlue guifg=Black
hi DokuDel                term=bold ctermbg=LightRed ctermfg=Black guibg=LightRed  guifg=Black
hi DokuList               term=bold cterm=bold ctermfg=Green gui=bold guifg=Green
hi DokuTableTH            term=bold cterm=bold ctermfg=Blue gui=bold guifg=Blue
hi DokuTableTD            term=bold cterm=bold ctermfg=Blue gui=bold guifg=Blue
hi DokuNoWiki             ctermbg=Gray ctermfg=Black guibg=Gray guifg=Black

" color groups
hi DokuBlockColor         ctermbg=Gray ctermfg=Black guibg=Gray guifg=Black
hi DokuFormatColor        cterm=bold ctermfg=Gray gui=bold guifg=Gray

" link to groups 
hi link DokuMonospaced    DokuFormatColor
hi link DokuFile          DokuBlockColor
hi link DokuCode          DokuBlockColor
hi link DokuCodeMatch     DokuBlockColor
hi link DokuFileMatch     DokuBlockColor
hi link DokuNoWiki        DokuBlockColor
hi link DokuFootnoteMatch DokuBlockColor

let b:current_syntax = "dokuwiki"

if main_syntax == 'dokuwiki'
  unlet main_syntax
endif

" vim:ts=2:sw=2:et:
