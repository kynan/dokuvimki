# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import re
import vim
import time

__version__ = '2010-07-01'
__author__ = 'Michael Klier <chi@chimeric.de>'

try:
    import dokuwikixmlrpc
    has_dokuwikixmlrpc = True
except ImportError:
    print('DokuVimKi Error: The dokuwikixmlrpc python module is missing!', file=sys.stderr)
    has_dokuwikixmlrpc = False

vim_version = int(vim.eval('v:version'))

if sys.version_info < (3,):
    def u(x):
        return x if isinstance(x, unicode) else x.decode('utf-8')
else:
    def u(x):
        return x


class DokuVimKi:
    """
    Provides all necessary functionality to interface between the DokuWiki
    XMLRPC API and vim.
    """

    def __init__(self):
        """
        Instantiates special buffers, setup the xmlrpc connection and loads the
        page index and displays the recent changes of the last 7 days.
        """

        if sys.version_info < (2, 4):
            print("DokuVimKi requires at least python Version 2.4 or greater!", file=sys.stderr)
            return

        if not has_dokuwikixmlrpc:
            print("dokuwikixmlrpc python module missing!", file=sys.stderr)
            return

        if self.xmlrpc_init():

            vim.command("command! -complete=customlist,CmdModeComplete -nargs=1 DWedit exec('Py dokuvimki.edit(<f-args>)')")
            vim.command("command! -complete=customlist,CmdModeComplete -nargs=* DWcd exec('Py dokuvimki.cd(<f-args>)')")
            vim.command("command! -nargs=? DWsave exec('Py dokuvimki.save(<f-args>)')")
            vim.command("command! -nargs=? DWsearch exec('Py dokuvimki.search(\"page\", <f-args>)')")
            vim.command("command! -nargs=? DWmediasearch exec('Py dokuvimki.search(\"media\", <f-args>)')")
            vim.command("command! -complete=customlist,CmdModeComplete -nargs=* DWrevisions exec('Py dokuvimki.revisions(<f-args>)')")
            vim.command("command! -complete=customlist,CmdModeComplete -nargs=? DWbacklinks exec('Py dokuvimki.backlinks(<f-args>)')")
            vim.command("command! -nargs=? DWchanges exec('Py dokuvimki.changes(<f-args>)')")
            vim.command("command! -nargs=0 -bang DWclose exec('Py dokuvimki.close(\"<bang>\")')")
            vim.command("command! -nargs=0 DWdiffclose exec('Py dokuvimki.diff_close()')")
            vim.command("command! -complete=file -bang -nargs=1 DWupload exec('Py dokuvimki.upload(<f-args>,\"<bang>\")')")
            vim.command("command! -nargs=0 DWhelp exec('Py dokuvimki.help()')")
            vim.command("command! -nargs=0 -bang DWquit exec('Py dokuvimki.quit(\"<bang>\")')")

            self.buffers = {}
            self.buffers['search'] = Buffer('search', 'nofile')
            self.buffers['backlinks'] = Buffer('backlinks', 'nofile')
            self.buffers['revisions'] = Buffer('revisions', 'nofile')
            self.buffers['changes'] = Buffer('changes', 'nofile')
            self.buffers['index'] = Buffer('index', 'nofile')
            self.buffers['media'] = Buffer('media', 'nofile')
            self.buffers['help'] = Buffer('help', 'nofile')

            self.needs_refresh = False
            self.diffmode = False

            self.cur_ns = ''
            self.pages = []

            self.default_sum = vim.eval('g:DokuVimKi_DEFAULT_SUM')

            self.index_winwith = vim.eval('g:DokuVimKi_INDEX_WINWIDTH')
            self.index(self.cur_ns, True)

            vim.command('set laststatus=2')
            vim.command('silent! ' + self.index_winwith + 'vsplit')
            self.help()

            vim.command("command! -nargs=0 DokuVimKi echo 'DokuVimKi is already running!'")

    def xmlrpc_init(self):
        """
        Establishes the xmlrpc connection to the remote wiki.
        """

        try:
            self.dw_user = vim.eval('g:DokuVimKi_USER')
            self.dw_pass = vim.eval('g:DokuVimKi_PASS')
            self.dw_url = vim.eval('g:DokuVimKi_URL')
        except vim.error as err:
            print("Error: %s. Please check your configuration settings." % err, file=sys.stderr)
            return False

        try:
            self.xmlrpc = dokuwikixmlrpc.DokuWikiClient(self.dw_url, self.dw_user, self.dw_pass)
            print('Connection to ' + vim.eval('g:DokuVimKi_URL') + ' established!', file=sys.stdout)
            return True
        except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
            print(err, file=sys.stderr)
            return False
        except dokuwikixmlrpc.DokuWikiURLError as err:
            print(err, file=sys.stderr)
            return False

    def edit(self, wp, rev=''):
        """
        Opens a given wiki page, or a given revision of a wiki page for
        editing or switches to the correct buffer if the is open already.
        """

        print("editing pagename %s." % wp, file=sys.stdout)
        wp = ':'.join([x.strip().lower().replace(' ', '_') for x in wp.split(':')])

        if self.diffmode:
            self.diff_close()

        self.focus(2)

        if wp.find(':') == -1:
            wp = self.cur_ns + wp

        if wp not in self.buffers:

            perm = int(self.xmlrpc.acl_check(wp))

            if perm >= 1:
                try:
                    if rev:
                        text = self.xmlrpc.page(wp, int(rev))
                    else:
                        text = self.xmlrpc.page(wp)
                except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
                    print(err, file=sys.stdout)

                if text:
                    if perm == 1:
                        print("You don't have permission to edit %s. Opening readonly!" % wp, file=sys.stderr)
                        self.buffers[wp] = Buffer(wp, 'nowrite', True)
                        self.buffers[wp].buf[:] = text.split("\n")
                        vim.command('setlocal nomodifiable')
                        vim.command('setlocal readonly')

                    if perm >= 2:
                        if not self.lock(wp):
                            return

                        print("Opening %s for editing ..." % wp, file=sys.stdout)
                        self.buffers[wp] = Buffer(wp, 'acwrite', True)
                        self.buffers[wp].page[:] = text.split("\n")
                        self.buffers[wp].buf[:] = self.buffers[wp].page

                        vim.command('set nomodified')
                        vim.command('autocmd! BufWriteCmd <buffer> Py dokuvimki.save()')
                        vim.command('autocmd! FileWriteCmd <buffer> Py dokuvimki.save()')
                        vim.command('autocmd! FileAppendCmd <buffer> Py dokuvimki.save()')

                if not text and perm >= 4:
                    print("Creating new page: %s" % wp, file=sys.stdout)
                    self.buffers[wp] = Buffer(wp, 'acwrite', True)
                    self.needs_refresh = True

                    vim.command('set nomodified')
                    vim.command('autocmd! BufWriteCmd <buffer> Py dokuvimki.save()')
                    vim.command('autocmd! FileWriteCmd <buffer> Py dokuvimki.save()')
                    vim.command('autocmd! FileAppendCmd <buffer> Py dokuvimki.save()')

                self.buffer_setup()

            else:
                print("You don't have permissions to read/edit/create %s" % wp, file=sys.stderr)
                return

        else:
            self.needs_refresh = False
            vim.command('silent! buffer! ' + self.buffers[wp].num)

    def diff(self, revline):
        """
        Opens a page and a given revision in diff mode.
        """

        data = revline.split()
        wp = data[0]
        rev = data[2]
        date = time.strftime('%Y-%m-%d@%Hh%mm%Ss', time.localtime(float(rev)))

        if wp not in self.buffers:
            self.edit(wp)

        if rev not in self.buffers[wp].diff:
            text = self.xmlrpc.page(wp, int(rev))
            if text:
                self.buffers[wp].diff[rev] = Buffer(wp + '_' + date, 'nofile')
                self.buffers[wp].diff[rev].page[:] = text.split("\n")
            else:
                print("Error, couldn't load revision for diffing.", file=sys.stdout)
                return

        self.focus(2)
        vim.command('silent! buffer! ' + self.buffers[wp].num)
        vim.command('vertical diffsplit')
        self.focus(3)
        vim.command('silent! buffer! ' + self.buffers[wp].diff[rev].num)
        vim.command('setlocal modifiable')
        vim.command('abbr <buffer> close DWdiffclose')
        vim.command('abbr <buffer> DWclose DWdiffclose')
        self.buffers[wp].diff[rev].buf[:] = self.buffers[wp].diff[rev].page
        vim.command('setlocal nomodifiable')
        self.buffer_setup()
        vim.command('diffthis')
        self.focus(2)
        self.diffmode = True

    def diff_close(self):
        """
        Closes the diff window.
        """

        self.focus(3)
        vim.command('diffoff')
        vim.command('close')
        self.diffmode = False
        self.focus(2)
        vim.command('vertical resize')

    def save(self, sum='', minor=0):
        """
        Saves the current buffer. Works only if the buffer is a wiki page.
        Deleting wiki pages works like using the web interface, just delete all
        text and save.
        """

        wp = vim.current.buffer.name.rsplit(os.sep, 1)[1]
        try:
            if not self.buffers[wp].iswp:
                print("Error: Current buffer %s is not a wiki page or not writeable!" % wp, file=sys.stderr)
            elif self.buffers[wp].type == 'nowrite':
                print("Error: Current buffer %s is readonly!" % wp, file=sys.stderr)
            else:
                text = "\n".join(self.buffers[wp].buf)
                if text and not self.ismodified(wp):
                    print("No unsaved changes in current buffer.", file=sys.stdout)
                elif not text and wp not in self.pages:
                    print("Can't save new empty page %s." % wp, file=sys.stdout)
                else:
                    if not sum and text:
                        sum = self.default_sum
                        minor = 1

                    try:
                        self.xmlrpc.put_page(wp, text, sum, minor)
                        self.buffers[wp].page[:] = self.buffers[wp].buf
                        self.buffers[wp].need_save = False

                        if text:
                            vim.command('silent! buffer! ' + self.buffers[wp].num)
                            vim.command('set nomodified')
                            print('Page %s written!' % wp, file=sys.stdout)

                            if self.needs_refresh:
                                self.index(self.cur_ns, True)
                                self.needs_refresh = False
                                self.focus(2)
                        else:
                            print('Page %s removed!' % wp, file=sys.stdout)
                            self.close(False)
                            self.index(self.cur_ns, True)
                            self.focus(2)

                    except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
                        print('DokuVimKi Error: %s' % err, file=sys.stderr)
        except KeyError as err:
            print("Error: Current buffer %s is not handled by DWsave!" % wp, file=sys.stderr)

    def upload(self, file, overwrite=False):
        """
        Uploads a file to the remote wiki.
        """

        path = os.path.realpath(file)
        fname = os.path.basename(path)

        if os.path.isfile(path):
            try:
                fh = open(path, 'r')
                data = fh.read()
                file_id = self.cur_ns + fname
                try:
                    self.xmlrpc.put_file(file_id, data, overwrite)
                    print("Uploaded %s successfully." % fname, file=sys.stdout)
                    self.refresh()
                except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
                    print(err, file=sys.stderr)
            except IOError as err:
                print(err, file=sys.stderr)
        else:
            print('%s is not a file' % path, file=sys.stderr)

    def cd(self, query=''):
        """
        Changes into the given namespace.
        """

        if query and query[-1] != ':':
            query += ':'

        self.index(query)

    def index(self, query='', refresh=False):
        """
        Build the index used to navigate the remote wiki.
        """

        index = []
        pages = []
        dirs = []

        self.focus(1)
        vim.command('set winwidth=' + self.index_winwith)
        vim.command('set winminwidth=' + self.index_winwith)

        vim.command('silent! buffer! ' + self.buffers['index'].num)
        vim.command('setlocal modifiable')
        vim.command('setlocal nonumber')
        vim.command('syn match DokuVimKi_NS /^.*\//')
        vim.command('syn match DokuVimKi_CURNS /^ns:/')

        vim.command('hi DokuVimKi_NS term=bold cterm=bold ctermfg=LightBlue gui=bold guifg=LightBlue')
        vim.command('hi DokuVimKi_CURNS term=bold cterm=bold ctermfg=Yellow gui=bold guifg=Yellow')

        if refresh:
            self.refresh()

        if query and query[-1] != ':':
            self.edit(query)
            return
        else:
            self.cur_ns = query

        if self.pages:
            for page in self.pages:
                if not query:
                    if page.find(':', 0) == -1:
                        pages.append(page)
                    else:
                        ns = page.split(':', 1)[0] + '/'
                        if ns not in dirs:
                            dirs.append(ns)
                else:
                    if re.search('^' + query, page):
                        page = page.replace(query, '')
                        if page.find(':') == -1:
                            if page not in index:
                                pages.append(page)
                        else:
                            ns = page.split(':', 1)[0] + '/'
                            if ns not in dirs:
                                dirs.append(ns)

            index.append('ns: ' + self.cur_ns)

            if query:
                index.append('.. (up a namespace)')

            index.append('')

            pages.sort()
            dirs.sort()
            index = index + dirs + pages

            self.buffers['index'].buf[:] = index

            vim.command('map <silent> <buffer> <enter> :Py dokuvimki.cmd("index")<CR>')
            vim.command('map <silent> <buffer> r :Py dokuvimki.cmd("revisions")<CR>')
            vim.command('map <silent> <buffer> b :Py dokuvimki.cmd("backlinks")<CR>')

            vim.command('setlocal nomodifiable')
            vim.command('2')

    def changes(self, timeframe=False):
        """
        Shows the last changes on the remote wiki.
        """

        if self.diffmode:
            self.diff_close()

        self.focus(2)

        vim.command('silent! buffer! ' + self.buffers['changes'].num)
        vim.command('setlocal modifiable')

        if not timeframe:
            timestamp = int(time.time()) - (60 * 60 * 24 * 7)
        else:
            m = re.match(r'(?P<num>\d+)(?P<type>[dw]{1})', timeframe)
            if m:
                argv = m.groupdict()

                if argv['type'] == 'd':
                    timestamp = int(time.time()) - (60 * 60 * 24 * int(argv['num']))
                elif argv['type'] == 'w':
                    timestamp = int(time.time()) - (60 * 60 * 24 * (int(argv['num']) * 7))
                else:
                    print("Wrong timeframe format %s." % timeframe, file=sys.stderr)
                    return
            else:
                print("Wrong timeframe format %s." % timeframe, file=sys.stderr)
                return

        try:
            changes = self.xmlrpc.recent_changes(timestamp)
            if len(changes) > 0:
                maxlen = max(len(change['name']) for change in changes)
                fmt = '{name:' + str(maxlen) + '}\t{lastModified}\t{version}\t{author}'
                self.buffers['changes'].buf[:] = list(reversed([fmt.format(**change) for change in changes]))
                vim.command('syn match DokuVimKi_REV_PAGE /^\(\w\|:\)*/')
                vim.command('syn match DokuVimKi_REV_TS /\s\d*\s/')

                vim.command('hi DokuVimKi_REV_PAGE cterm=bold ctermfg=Yellow gui=bold guifg=Yellow')
                vim.command('hi DokuVimKi_REV_TS cterm=bold ctermfg=Yellow gui=bold guifg=Yellow')

                vim.command('setlocal nomodifiable')
                vim.command('map <silent> <buffer> <enter> :Py dokuvimki.rev_edit()<CR>')

            else:
                print('DokuVimKi Error: No changes', file=sys.stderr)

        except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
            print(err, file=sys.stderr)

    def revisions(self, wp='', first=0):
        """
        Display revisions for a certain page if any.
        """

        if self.diffmode:
            self.diff_close()

        if not wp or wp[-1] == ':':
            return

        try:
            self.focus(2)

            vim.command('silent! buffer! ' + self.buffers['revisions'].num)
            vim.command('setlocal modifiable')

            revs = self.xmlrpc.page_versions(wp, int(first))
            if revs:
                self.buffers['revisions'].buf[:] = [wp + "\t" + "\t".join(str(rev[x]) for x in ['modified', 'version', 'ip', 'type', 'user', 'sum'])
                                                    for rev in revs]
                print("loaded revisions for :%s" % wp, file=sys.stdout)
                vim.command('map <silent> <buffer> <enter> :Py dokuvimki.rev_edit()<CR>')

                vim.command('syn match DokuVimKi_REV_PAGE /^\(\w\|:\)*/')
                vim.command('syn match DokuVimKi_REV_TS /\s\d*\s/')
                vim.command('syn match DokuVimKi_REV_CHANGE /\s\w\{1}\s/')

                vim.command('hi DokuVimKi_REV_PAGE term=bold cterm=bold ctermfg=Yellow gui=bold guifg=Yellow')
                vim.command('hi DokuVimKi_REV_TS term=bold cterm=bold ctermfg=Yellow gui=bold guifg=Yellow')
                vim.command('hi DokuVimKi_REV_CHANGE term=bold cterm=bold ctermfg=Yellow gui=bold guifg=Yellow')

                vim.command('setlocal nomodifiable')
                vim.command('map <silent> <buffer> d :Py dokuvimki.cmd("diff")<CR>')

            else:
                print('DokuVimKi Error: No revisions found for page: %s' % wp, file=sys.stderr)

        except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
            print('DokuVimKi XML-RPC Error: %s' % err, file=sys.stderr)

    def backlinks(self, wp=''):
        """
        Display backlinks for a certain page if any.
        """

        if self.diffmode:
            self.diff_close()

        if not wp or wp[-1] == ':':
            return

        try:
            self.focus(2)

            vim.command('silent! buffer! ' + self.buffers['backlinks'].num)
            vim.command('setlocal modifiable')

            blinks = self.xmlrpc.backlinks(wp)

            if len(blinks) > 0:
                for link in blinks:
                    self.buffers['backlinks'].buf[:] = map(str, blinks)
                vim.command('map <buffer> <enter> :Py dokuvimki.cmd("edit")<CR>')
            else:
                print('DokuVimKi Error: No backlinks found for page: %s' % wp, file=sys.stderr)

            vim.command('setlocal nomodifiable')

        except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
            print('DokuVimKi XML-RPC Error: %s' % err, file=sys.stderr)

    def search(self, type='', pattern=''):
        """
        Search the page list for matching pages and display them for editing.
        """

        if self.diffmode:
            self.diff_close()

        self.focus(2)

        try:
            if type == 'page':
                vim.command('silent! buffer! ' + self.buffers['search'].num)
                vim.command('setlocal modifiable')

                if pattern:
                    p = re.compile(pattern)
                    result = filter(p.search, self.pages)
                else:
                    result = self.pages

                if len(result) > 0:
                    self.buffers['search'].buf[:] = result
                    vim.command('map <buffer> <enter> :Py dokuvimki.cmd("edit")<CR>')
                else:
                    print('DokuVimKi Error: No matching pages found!', file=sys.stderr)

            elif type == 'media':
                vim.command('silent! buffer! ' + self.buffers['media'].num)
                vim.command('setlocal modifiable')

                if pattern:
                    p = re.compile(pattern)
                    result = filter(p.search, self.media)
                else:
                    result = self.media

                if len(result) > 0:
                    self.buffers['media'].buf[:] = result
                else:
                    print('DokuVimKi Error: No matching media files found!', file=sys.stderr)

            vim.command('setlocal nomodifiable')

        except:
            pass

    def close(self, bang):
        """
        Closes the current buffer. Works only if the current buffer is a wiki
        page.  The buffer is also removed from the buffer stack.
        """

        if self.diffmode:
            self.diff_close()
            return

        try:
            buffer = vim.current.buffer.name.rsplit(os.sep, 1)[1]
            if self.buffers[buffer].iswp:
                if not bang and self.ismodified(buffer):
                    print("Warning: %s contains unsaved changes! Use DWclose!." % buffer, file=sys.stderr)
                    return

                vim.command('bp!')
                vim.command('bdel! ' + self.buffers[buffer].num)
                if self.buffers[buffer].type == 'acwrite':
                    self.unlock(buffer)
                del self.buffers[buffer]
            else:
                print('You cannot close special buffer "%s"!' % buffer, file=sys.stderr)

        except KeyError:
            print('You cannot use DWclose on non wiki page "%s"!' % buffer, file=sys.stderr)

    def quit(self, bang):
        """
        Quits the current session.
        """

        unsaved = []

        for buffer in list(self.buffers):
            if self.buffers[buffer].iswp:
                if not self.ismodified(buffer):
                    vim.command('silent! buffer! ' + self.buffers[buffer].num)
                    self.close(False)
                elif self.ismodified(buffer) and bang:
                    vim.command('silent! buffer! ' + self.buffers[buffer].num)
                    self.close(True)
                else:
                    unsaved.append(buffer)

        if len(unsaved) == 0:
            vim.command('silent! quitall')
        else:
            print("Some buffers contain unsaved changes. Use DWquit! if you really want to quit.", file=sys.stderr)

    def help(self):
        """
        Shows the plugin help.
        """

        if self.diffmode:
            self.diff_close()

        self.focus(2)
        vim.command('silent! buffer! ' + self.buffers['help'].num)
        vim.command('silent! set buftype=help')

        vim.command('help dokuvimki')
        vim.command("setlocal statusline=%{'[help]'}")

    def ismodified(self, buffer):
        """
        Checks whether the current buffer or a given buffer is modified or not.
        """

        if self.buffers[buffer].need_save:
            return True
        elif u("\n".join(self.buffers[buffer].page).strip()) != u("\n".join(self.buffers[buffer].buf).strip()):
            return True
        else:
            return False

    def rev_edit(self):
        """
        Special mapping for editing revisions from the revisions listing.
        """

        row, col = vim.current.window.cursor
        wp = vim.current.buffer[row - 1].split("\t")[0].strip()
        rev = vim.current.buffer[row - 1].split("\t")[2].strip()
        self.edit(wp, rev)

    def focus(self, winnr):
        """
        Convenience function to switch the current window focus.
        """

        if int(vim.eval('winnr()')) != winnr:
            vim.command(str(winnr) + 'wincmd w')

    def refresh(self):
        """
        Refreshes the page index by retrieving a fresh list of all pages on the
        remote server and updating the completion dictionary.
        """

        self.pages = []
        self.media = []

        try:
            print("Refreshing page index!", file=sys.stdout)
            data = self.xmlrpc.all_pages()

            if data:
                for page in data:
                    page = page['id']
                    ns = page.rsplit(':', 1)[0] + ':'
                    self.pages.append(page)
                    if ns not in self.pages:
                        self.pages.append(ns)
                        self.media.append(ns)

            self.pages.sort()
            vim.command('let g:pages = "' + " ".join(self.pages) + '"')

            print("Refreshing media index!", file=sys.stdout)
            data = self.xmlrpc.list_files(':', True)

            if data:
                for media in data:
                    self.media.append(media['id'])

            self.media.sort()
            vim.command('let g:media = "' + " ".join(self.media) + '"')

        except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
            print("Failed to fetch page list. Please check your configuration\n%s" % err, file=sys.stderr)

    def lock(self, wp):
        """
        Tries to obtain a lock given wiki page.
        """

        locks = {}
        locks['lock'] = [wp]
        locks['unlock'] = []

        result = self.set_locks(locks)

        if locks['lock'] == result['locked']:
            print("Locked page %s for editing." % wp, file=sys.stdout)
            return True
        else:
            print('The page "%s" appears to be locked for editing. You have to wait until the lock expires.' % wp, file=sys.stderr)
            return False

    def unlock(self, wp):
        """
        Tries to unlock a given wiki page.
        """

        locks = {}
        locks['lock'] = []
        locks['unlock'] = [wp]

        result = self.set_locks(locks)

        if locks['unlock'] == result['unlocked']:
            return True
        else:
            return False

    def set_locks(self, locks):
        """
        Locks unlocks a given set of pages.
        """

        try:
            return self.xmlrpc.set_locks(locks)
        except dokuwikixmlrpc.DokuWikiXMLRPCError as err:
            print(err, file=sys.stderr)

    def id_lookup(self):
        """
        When editing pages, hiting enter while over a wiki link will open the
        page. This functions tries to guess the correct wiki page.
        """
        line = vim.current.line
        row, col = vim.current.window.cursor

        # get namespace from current page
        wp = vim.current.buffer.name.rsplit(os.sep, 1)[1]
        ns = wp.rsplit(':', 1)[0]
        if ns == wp:
            ns = ''

        # look for link syntax on the left and right from the current curser position
        reL = re.compile('\[{2}[^]]*$')  # opening link syntax
        reR = re.compile('^[^\[]*]{2}')  # closing link syntax

        L = reL.search(line[:col])
        R = reR.search(line[col:])

        # if both matched we probably have a link
        if L and R:

            # sanitize match remove anchors and everything after '|'
            id = (L.group() + R.group()).strip('[]').split('|')[0].split('#')[0]

            # check if it's not and external/interwiki/share link
            if id.find('>') == -1 and id.find('://') == -1 and id.find('\\') == -1:

                # check if useshlash is used
                if id.find('/'):
                    id = id.replace('/', ':')

                # this is _almost_ a rip off of DokuWikis resolve_id() function
                if id[0] == '.':
                    re_sanitize = re.compile('(\.(?=[^:\.]))')
                    id = re_sanitize.sub('.:', id)
                    id = ns + ':' + id
                    path = id.split(':')

                    result = []
                    for dir in path:
                        if dir == '..':
                            try:
                                if result[-1] == '..':
                                    result.append('..')
                                elif not result.pop():
                                    result.append('..')
                            except IndexError:
                                pass
                        elif dir and dir != '.' and not len(dir.split('.')) > 2:
                            result.append(dir)

                    id = ':'.join(result)

                elif ns and id[0] != ':' and id.find(':', 0) == -1:
                    id = ns + ':' + id

                # we're done, open the page for editing
                print(id, file=sys.stdout)
                self.edit(id)

    def cmd(self, cmd):
        """
        Callback function to provides various functionality for the page index
        (like open namespaces or triggering edit showing backlinks etc).
        """

        row, col = vim.current.window.cursor
        line = vim.current.buffer[row - 1]

        # first line triggers nothing in index buffer
        if row == 1 and line.find('ns: ') != -1:
            return

        if line.find('..') == -1:
            if line.find('/') == -1:
                if not line:
                    print("meh", file=sys.stdout)
                else:
                    line = self.cur_ns + line
            else:
                line = self.cur_ns + line.replace('/', ':')
        else:
            line = self.cur_ns.rsplit(':', 2)[0] + ':'
            if line == ":" or line == self.cur_ns:
                line = ''

        callback = getattr(self, cmd)
        callback(line)

    def buffer_enter(self, wp):
        """
        Loads the buffer on enter.
        """

        self.buffers[wp].buf[:] = self.buffers[wp].page
        vim.command('setlocal nomodified')
        self.buffer_setup()

    def buffer_leave(self, wp):
        if "\n".join(self.buffers[wp].buf).strip() != "\n".join(self.buffers[wp].page).strip():
            self.buffers[wp].page[:] = self.buffers[wp].buf
            self.buffers[wp].need_save = True

    def buffer_setup(self):
        """
        Setup edit environment.
        """

        vim.command('setlocal textwidth=0')
        vim.command('setlocal wrap')
        vim.command('setlocal linebreak')
        vim.command('setlocal syntax=dokuwiki')
        vim.command('setlocal filetype=dokuwiki')
        vim.command('setlocal tabstop=2')
        vim.command('setlocal expandtab')
        vim.command('setlocal shiftwidth=2')
        vim.command('setlocal encoding=utf-8')
        vim.command('setlocal completefunc=InsertModeComplete')
        vim.command('setlocal omnifunc=InsertModeComplete')
        vim.command('map <buffer> <silent> <C-]> :Py dokuvimki.id_lookup()<CR>')
        vim.command('imap <buffer> <silent> <C-D><C-B> ****<ESC>1hi')
        vim.command('imap <buffer> <silent> <C-D><C-I> ////<ESC>1hi')
        vim.command('imap <buffer> <silent> <C-D><C-U> ____<ESC>1hi')
        vim.command('imap <buffer> <silent> <C-D><C-L> [[]]<ESC>1hi')
        vim.command('imap <buffer> <silent> <C-D><C-M> {{}}<ESC>1hi')
        vim.command('imap <buffer> <silent> <C-D><C-K> <code><CR><CR></code><ESC>ki')
        vim.command('imap <buffer> <silent> <C-D><C-F> <file><CR><CR></file><ESC>ki')
        vim.command('imap <buffer> <silent> <expr> <C-D><C-H> Headline()')
        vim.command('imap <buffer> <silent> <expr> <C-D><C-P> SetLvl(+1)')
        vim.command('imap <buffer> <silent> <expr> <C-D><C-D> SetLvl(-1)')


class Buffer:
    """
    Representates a vim buffer object. Used to manage keep track of all opened
    pages and to handle the dokuvimki special buffers.

        self.num    = buffer number (starts at 1)
        self.id     = buffer id (starts at 0)
        self.buf    = vim buffer object
        self.name   = buffer name
        self.iswp   = True if buffer represents a wiki page
    """

    id = None
    num = None
    name = None
    buf = None

    def __init__(self, name, type, iswp=False):
        """
        Instanziates a new buffer.
        """
        vim.command('badd ' + name)
        self.num = vim.eval('bufnr("' + name + '")')

        # buffers are numbered from 0 in vim 7.3 and older
        # and from 1 in vim 7.4 and newer
        self.id = int(self.num)
        if vim_version < 704:
            self.id -= 1

        self.buf = vim.buffers[self.id]
        self.name = name
        self.iswp = iswp
        self.type = type
        self.page = []
        vim.command('silent! buffer! ' + self.num)
        vim.command('setlocal buftype=' + type)
        vim.command('abbr <silent> close DWclose')
        vim.command('abbr <silent> close! DWclose!')
        vim.command('abbr <silent> quit DWquit')
        vim.command('abbr <silent> quit! DWquit!')
        vim.command('abbr <silent> q DWquit')
        vim.command('abbr <silent> q! DWquit!')
        vim.command('abbr <silent> qa DWquit')
        vim.command('abbr <silent> qa! DWquit!')

        if type == 'nofile':
            vim.command('setlocal nobuflisted')
            vim.command('setlocal nomodifiable')
            vim.command('setlocal noswapfile')
            vim.command("setlocal statusline=%{'[" + self.name + "]'}")

        if type == 'acwrite':
            self.diff = {}
            self.need_save = False
            vim.command('autocmd! BufEnter <buffer> Py dokuvimki.buffer_enter("' + self.name + '")')
            vim.command('autocmd! BufLeave <buffer> Py dokuvimki.buffer_leave("' + self.name + '")')
            vim.command("setlocal statusline=%{'[wp]\ " + self.name + "'}\ %r\ [%c,%l][%p]")

        if type == 'nowrite':
            self.diff = {}
            vim.command("setlocal statusline=%{'[wp]\ " + self.name + "'}\ %r\ [%c,%l][%p%%]")