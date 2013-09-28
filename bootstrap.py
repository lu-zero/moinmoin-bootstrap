# -*- coding: utf-8 -*-
"""
    MoinMoin - bootstrap theme, based on codereading5

    @copyright: 2012 speirs http://www.codereading.com
    @copyright: 2013 Luca Barbato

    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.theme import ThemeBase
from MoinMoin.action import get_available_actions

from MoinMoin import wikiutil, config, version, caching
from MoinMoin.Page import Page

class Theme(ThemeBase):

    name = "bootstrap"

    _ = lambda x: x     # We don't have gettext at this moment, so we fake it
    icons = {
        # key         alt                        icon filename      w   h
        # FileAttach
        'attach':     ("%(attach_count)s",       "moin-attach.png",   16, 16),
        'info':       ("[INFO]",                 "moin-info.png",     16, 16),
        'attachimg':  (_("[ATTACH]"),            "attach.png",        32, 32),
        # RecentChanges
        'rss':        (_("[RSS]"),               "moin-rss.png",      16, 16),
        'deleted':    (_("[DELETED]"),           "moin-deleted.png",  16, 16),
        'updated':    (_("[UPDATED]"),           "moin-updated.png",  16, 16),
        'renamed':    (_("[RENAMED]"),           "moin-renamed.png",  16, 16),
        'conflict':   (_("[CONFLICT]"),          "moin-conflict.png", 16, 16),
        'new':        (_("[NEW]"),               "moin-new.png",      16, 16),
        'diffrc':     (_("[DIFF]"),              "moin-diff.png",     16, 16),
        # General
        'bottom':     (_("[BOTTOM]"),            "moin-bottom.png",   16, 16),
        'top':        (_("[TOP]"),               "moin-top.png",      16, 16),
        'www':        ("[WWW]",                  "moin-www.png",      16, 16),
        'mailto':     ("[MAILTO]",               "moin-email.png",    16, 16),
        'news':       ("[NEWS]",                 "moin-news.png",     16, 16),
        'telnet':     ("[TELNET]",               "moin-telnet.png",   16, 16),
        'ftp':        ("[FTP]",                  "moin-ftp.png",      16, 16),
        'file':       ("[FILE]",                 "moin-ftp.png",      16, 16),
        # search forms
        'searchbutton': ("[?]",                  "moin-search.png",   16, 16),
        'interwiki':  ("[%(wikitag)s]",          "moin-inter.png",    16, 16),
    }

    del _

    stylesheets = (
            # media     basename
            ('all',     'ui'),
            ('all',     'bootstrap'),
            ('all',     'pygments'),
            ('all',     'bs'),
            ('all',     'libav'),
            ('all',     'alert'),
            )


    def send_title(self, text, **keywords):
        """ Override
        Output the page header (and title).

        @param text: the title text
        @keyword page: the page instance that called us - using this is more efficient than using pagename..
        @keyword pagename: 'PageName'
        @keyword print_mode: 1 (or 0)
        @keyword editor_mode: 1 (or 0)
        @keyword media: css media type, defaults to 'screen'
        @keyword allow_doubleclick: 1 (or 0)
        @keyword html_head: additional <head> code
        @keyword body_attr: additional <body> attributes
        @keyword body_onload: additional "onload" JavaScript code
        """
        request = self.request
        _ = request.getText
        rev = request.rev

        if keywords.has_key('page'):
            page = keywords['page']
            pagename = page.page_name
        else:
            pagename = keywords.get('pagename', '')
            page = Page(request, pagename)
        if keywords.get('msg', ''):
            raise DeprecationWarning("Using send_page(msg=) is deprecated! Use theme.add_msg() instead!")
        scriptname = request.script_root

        # get name of system pages
        page_front_page = wikiutil.getFrontPage(request).page_name
        page_help_contents = wikiutil.getLocalizedPage(request, 'HelpContents').page_name
        page_title_index = wikiutil.getLocalizedPage(request, 'TitleIndex').page_name
        page_site_navigation = wikiutil.getLocalizedPage(request, 'SiteNavigation').page_name
        page_word_index = wikiutil.getLocalizedPage(request, 'WordIndex').page_name
        page_help_formatting = wikiutil.getLocalizedPage(request, 'HelpOnFormatting').page_name
        page_find_page = wikiutil.getLocalizedPage(request, 'FindPage').page_name
        home_page = wikiutil.getInterwikiHomePage(request) # sorry theme API change!!! Either None or tuple (wikiname,pagename) now.
        page_parent_page = getattr(page.getParentPage(), 'page_name', None)

        # set content_type, including charset, so web server doesn't touch it:
        request.content_type = "text/html; charset=%s" % (config.charset, )

        # Prepare the HTML <head> element
        user_head = [request.cfg.html_head]

        # include charset information - needed for moin_dump or any other case
        # when reading the html without a web server
        user_head.append('''<meta charset="%s">\n''' % (page.output_charset))

        meta_keywords = request.getPragma('keywords')
        meta_desc = request.getPragma('description')
        if meta_keywords:
            user_head.append('<meta name="keywords" content="%s">\n' % wikiutil.escape(meta_keywords, 1))
        if meta_desc:
            user_head.append('<meta name="description" content="%s">\n' % wikiutil.escape(meta_desc, 1))

        #  add meta statement if user has doubleclick on edit turned on or it is default
        if (pagename and keywords.get('allow_doubleclick', 0) and
            not keywords.get('print_mode', 0) and
            request.user.edit_on_doubleclick):
            if request.user.may.write(pagename): # separating this gains speed
                user_head.append('<meta name="edit_on_doubleclick" content="%s">\n' % (request.script_root or '/'))

        # search engine precautions / optimization:
        # if it is an action or edit/search, send query headers (noindex,nofollow):
        if request.query_string:
            user_head.append(request.cfg.html_head_queries)
        elif request.method == 'POST':
            user_head.append(request.cfg.html_head_posts)
        # we don't want to have BadContent stuff indexed:
        elif pagename in ['BadContent', 'LocalBadContent', ]:
            user_head.append(request.cfg.html_head_posts)
        # if it is a special page, index it and follow the links - we do it
        # for the original, English pages as well as for (the possibly
        # modified) frontpage:
        elif pagename in [page_front_page, request.cfg.page_front_page,
                          page_title_index, 'TitleIndex',
                          page_find_page, 'FindPage',
                          page_site_navigation, 'SiteNavigation',
                          'RecentChanges', ]:
            user_head.append(request.cfg.html_head_index)
        # if it is a normal page, index it, but do not follow the links, because
        # there are a lot of illegal links (like actions) or duplicates:
        else:
            user_head.append(request.cfg.html_head_normal)

        if 'pi_refresh' in keywords and keywords['pi_refresh']:
            user_head.append('<meta http-equiv="refresh" content="%d;URL=%s">' % keywords['pi_refresh'])

        # output buffering increases latency but increases throughput as well
        output = []
        output.append("""\
<!DOCTYPE html>
<html lang="%s">
<head>
%s
<meta name="viewport" content="width=device-width, initial-scale=1.0">
%s
%s
""" % (
            self.cfg.language_default,
            ''.join(user_head),
            self.html_head({
                'page': page,
                'title': text,
                'sitename': request.cfg.html_pagetitle or request.cfg.sitename,
                'print_mode': keywords.get('print_mode', False),
                'media': keywords.get('media', 'screen'),
            }),
            keywords.get('html_head', ''),
        ))

        output.append("</head>\n")
        request.write(''.join(output))
        output = []

        # start the <body>
        bodyattr = []
        if keywords.has_key('body_attr'):
            bodyattr.append(' ')
            bodyattr.append(keywords['body_attr'])

        # Set body to the user interface language and direction
        bodyattr.append(' %s' % self.ui_lang_attr())

        body_onload = keywords.get('body_onload', '')
        if body_onload:
            bodyattr.append(''' onload="%s"''' % body_onload)
        output.append('\n<body%s>\n' % ''.join(bodyattr))

        # Output -----------------------------------------------------------

        # If in print mode, start page div and emit the title
        if keywords.get('print_mode', 0):
            d = {
                'title_text': text,
                'page': page,
                'page_name': pagename or '',
                'rev': rev,
            }
            request.themedict = d
            output.append(self.startPage())
            output.append(self.interwiki(d))
            output.append(self.title(d))

        # In standard mode, emit theme.header
        else:
            exists = pagename and page.exists(includeDeleted=True)
            # prepare dict for theme code:
            d = {
                'theme': self.name,
                'script_name': scriptname,
                'title_text': text,
                'logo_string': request.cfg.logo_string,
                'site_name': request.cfg.sitename,
                'page': page,
                'rev': rev,
                'pagesize': pagename and page.size() or 0,
                # exists checked to avoid creation of empty edit-log for non-existing pages
                'last_edit_info': exists and page.lastEditInfo() or '',
                'page_name': pagename or '',
                'page_find_page': page_find_page,
                'page_front_page': page_front_page,
                'home_page': home_page,
                'page_help_contents': page_help_contents,
                'page_help_formatting': page_help_formatting,
                'page_parent_page': page_parent_page,
                'page_title_index': page_title_index,
                'page_word_index': page_word_index,
                'user_name': request.user.name,
                'user_valid': request.user.valid,
                'msg': self._status,
                'trail': keywords.get('trail', None),
                # Discontinued keys, keep for a while for 3rd party theme developers
                'titlesearch': 'use self.searchform(d)',
                'textsearch': 'use self.searchform(d)',
                'navibar': ['use self.navibar(d)'],
                'available_actions': ['use self.request.availableActions(page)'],
            }

            # add quoted versions of pagenames
            newdict = {}
            for key in d:
                if key.startswith('page_'):
                    if not d[key] is None:
                        newdict['q_'+key] = wikiutil.quoteWikinameURL(d[key])
                    else:
                        newdict['q_'+key] = None
            d.update(newdict)
            request.themedict = d

            # now call the theming code to do the rendering
            if keywords.get('editor_mode', 0):
                output.append(self.editorheader(d))
            else:
                output.append(self.header(d))

        # emit it
        request.write(''.join(output))
        output = []
        self._send_title_called = True
    #end def send_title

    def recentchanges_header(self, d):
        """ Override """
        html = ThemeBase.recentchanges_header(self,d)
        return html.replace('<table>', '<table class="table table-bordered">')
    #end def recentchanges_header

    def header(self, d, **keywords):
        """ Override - Assemble wiki header

        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            self.bs_site_header(d),
            self.bs_breadcrumb(d),
            self.bs_container_start(),
            self.bs_msg(d),
            self.bs_page_header(d),
            ]
        return '\n'.join(html)
    #end def header
    editorheader = header

    def footer(self, d, **keywords):
        """ Override Assemble wiki footer
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        html = [
                self.bs_footer(),
                self.bs_container_end(),
                self.bs_footer_js(),
                ]
        return u'\n'.join(html)
    #end def footer


    def startPage(self):
        """ Override """
        return u''
    #end def startPage


    def endPage(self):
        """ Override """
        return u''
    #end def endPage

    def html_head(self, d):
        """ Override - Assemble html head

        @param d: parameter dictionary
        @rtype: unicode
        @return: html head
        """
        html = [
            u'<title>%s</title>' % self.bs_custom_title(d),
            self.externalScript('common'),
            self.headscript(d), # Should move to separate .js file
            self.guiEditorScript(d),
            self.bs_html_stylesheets(d),
            self.rsslink(d),
            self.bs_html5_magic(),
            self.bs_google_analytics()
            ]
        return u'\n'.join(html)
    #end def html_head

    def bs_actions(self, page):
        """ Create actions menu list and items data dict
        @param page: current page, Page object
        @rtype: unicode
        @return: actions menu html fragment
        """
        html = []
        request = self.request
        _ = request.getText
        rev = request.rev

        menu = [
            'raw',
            'print',
            'RenderAsDocbook',
            'refresh',
            '__separator__',
            'SpellCheck',
            'LikePages',
            'LocalSiteMap',
            '__separator__',
            'RenamePage',
            'CopyPage',
            'DeletePage',
            '__separator__',
            'MyPages',
            'SubscribeUser',
            '__separator__',
            'Despam',
            'revert',
            'PackagePages',
            'SyncPages',
            ]

        # TODO use glyph-icons
        titles = {
            # action: menu title
            '__separator__': '',
            'raw':   _('Raw Text'),
            'print': _('Print View'),
            'refresh': _('Delete Cache'),
            'SpellCheck': _('Check Spelling'), # rename action!
            'RenamePage': _('Rename Page'),
            'CopyPage': _('Copy Page'),
            'DeletePage': _('Delete Page'),
            'LikePages': _('Like Pages'),
            'LocalSiteMap': _('Local Site Map'),
            'MyPages': _('My Pages'),
            'SubscribeUser': _('Subscribe User'),
            'Despam': _('Remove Spam'),
            'revert': _('Revert to this revision'),
            'PackagePages': _('Package Pages'),
            'RenderAsDocbook': _('Render as Docbook'),
            'SyncPages': _('Sync Pages'),
            }

        html.append(u'<div class="btn-group">')
        html.append(u'<a class="btn btn-mini dropdown-toggle" data-toggle="dropdown">')
        html.append(_('More Actions'))
        html.append(u'<span class="caret"></span>')
        html.append(u'</a>')
        html.append(u'<ul class="dropdown-menu">')

        option = '<li%(state)s><a href="'
        option += self.request.href(page.page_name)
        option += u'?action=%(action)s'
        if rev:
            option += u'&rev=%s' % rev
        option += u'">%(title)s</a><li>'

        disabled = u' class="disabled"'

        separator = u'<li class="divider"></li>'

        # Format standard actions
        available = get_available_actions(request.cfg, page, request.user)
        for action in menu:
            data = {'action': action,
                    'state' : u'',
                    'title' : titles[action]}
            # removes excluded actions from the more actions menu
            if action in request.cfg.actions_excluded:
                continue

            # Enable delete cache only if page can use caching
            if action == 'refresh':
                if not page.canUseCache():
                    data['action'] = 'show'
                    data['state'] = disabled

            # revert action enabled only if user can revert
            if action == 'revert' and not request.user.may.revert(page.page_name):
                data['action'] = 'show'
                data['state'] = disabled

            # SubscribeUser action enabled only if user has admin rights
            if action == 'SubscribeUser' and not request.user.may.admin(page.page_name):
                data['action'] = 'show'
                data['state'] = disabled

            # Despam action enabled only for superusers
            if action == 'Despam' and not request.user.isSuperUser():
                data['action'] = 'show'
                data['state'] = disabled

            # Special menu items. Without javascript, executing will
            # just return to the page.
            if action.startswith('__'):
                data['action'] = 'show'

            # Actions which are not available for this wiki, user or page
            if (action == '__separator__'):
                html.append(separator)
                continue

            if (action[0].isupper() and not action in available):
                data['state'] = disabled

            html.append(option % data)

        # Add custom actions not in the standard menu, except for
        # some actions like AttachFile (we have them on top level)
        more = [item for item in available if not item in titles and not item in ('AttachFile', )]
        more.sort()
        if more:
            # Add separator
            html.append(separator)
            # Add more actions (all enabled)
            for action in more:
                data = {'action': action, 'state': ''}
                # Always add spaces: AttachFile -> Attach File
                # XXX do not create page just for using split_title -
                # creating pages for non-existent does 2 storage lookups
                #title = Page(request, action).split_title(force=1)
                title = action
                # Use translated version if available
                data['title'] = _(title)
                html.append(option % data)

        html.append(u'</ul></div>')

        return u'\n'.join(html)

    def bs_discussion(self, page):
        """Return a button to the discussion page
        """
        _ = self.request.getText
        suppl_name = self.request.cfg.supplementation_page_name
        suppl_name_full = "%s/%s" % (page.page_name, suppl_name)

        return page.link_to(self.request, text=_(suppl_name),
                            querystr={'action': 'supplementation'},
                            css_class='btn btn-mini', rel='nofollow')

    def bs_edit(self, page):
        """ Return an edit button to

        If the user want to show both editors, it will display "Edit
        (Text)", otherwise as "Edit".
        """
        if 'edit' in self.request.cfg.actions_excluded:
            return ""

        css_class = u'btn btn-mini'

        if not (page.isWritable() and
                self.request.user.may.write(page.page_name)):
            css_class += u' disabled'

        _ = self.request.getText
        querystr = {'action': 'edit'}

        guiworks = self.guiworks(page)
        text = _('Edit')
        if guiworks:
            # 'textonly' will be upgraded dynamically to 'guipossible' by JS
            querystr['editor'] = 'textonly'
            attrs = {'name': 'editlink',
                     'rel': 'nofollow',
                     'css_class': css_class}
        else:
            querystr['editor'] = 'text'
            attrs = {'name': 'texteditlink',
                     'rel': 'nofollow',
                     'css_class': css_class}

        return page.link_to(self.request, text=text, querystr=querystr, **attrs)

    def bs_info(self, page):
        """ Return link to page information """
        if 'info' in self.request.cfg.actions_excluded:
            return ""

        _ = self.request.getText
        return page.link_to(self.request,
                            text=_('Info'),
                            querystr={'action': 'info'},
                            css_class='btn btn-mini', rel='nofollow')

    def bs_subscribe(self, page):
        """ Return subscribe/unsubscribe link to valid users

        @rtype: unicode
        @return: subscribe or unsubscribe link
        """
        if not ((self.cfg.mail_enabled or self.cfg.jabber_enabled) and self.request.user.valid):
            return ''

        _ = self.request.getText
        if self.request.user.isSubscribedTo([page.page_name]):
            action, text = 'unsubscribe', _("Unsubscribe")
        else:
            action, text = 'subscribe', _("Subscribe")
        if action in self.request.cfg.actions_excluded:
            return ""
        return page.link_to(self.request, text=text,
                            querystr={'action': action},
                            css_class='btn btn-mini', rel='nofollow')

    def bs_quicklink(self, page):
        """ Return add/remove quicklink link

        @rtype: unicode
        @return: link to add or remove a quicklink
        """
        if not self.request.user.valid:
            return ''

        _ = self.request.getText
        if self.request.user.isQuickLinkedTo([page.page_name]):
            action, text = 'quickunlink', _("Remove Link")
        else:
            action, text = 'quicklink', _("Add Link")
        if action in self.request.cfg.actions_excluded:
            return ""
        return page.link_to(self.request, text=text,
                            querystr={'action': action},
                            css_class='btn btn-mini', rel='nofollow')

    def bs_attachments(self, page):
        """ Return link to page attachments """
        if 'AttachFile' in self.request.cfg.actions_excluded:
            return ""

        _ = self.request.getText
        return page.link_to(self.request,
                            text=_('Attachments'),
                            querystr={'action': 'AttachFile'},
                            css_class='btn btn-mini', rel='nofollow')

    def disabledEdit(self):
        """ Return a disabled edit link """
        _ = self.request.getText
        return ('<span class="disabled">%s</span>'
                % _('Immutable Page'))


    def editbarItems(self, page):
        """ Return list of items to show on the editbar

        This is separate method to make it easy to customize the
        editbar in sub classes.
        """
        _ = self.request.getText
        editbar_actions = []
        for editbar_item in self.request.cfg.edit_bar:
            if (editbar_item == 'Discussion' and
               (self.request.getPragma('supplementation-page', self.request.cfg.supplementation_page)
                                                   in (True, 1, 'on', '1'))):
                    editbar_actions.append(self.bs_discussion(page))
            elif editbar_item == 'Comments':
                # we just use <a> to get same style as other links, but we add some dummy
                # link target to get correct mouseover pointer appearance. return false
                # keeps the browser away from jumping to the link target::
                editbar_actions.append('<a href="#" class="btn btn-mini toggleCommentsButton" onClick="toggleComments();return false;" style="display:none;">%s</a>' % _('Comments'))
            elif editbar_item == 'Edit':
                editbar_actions.append(self.bs_edit(page))
            elif editbar_item == 'Info':
                editbar_actions.append(self.bs_info(page))
            elif editbar_item == 'Subscribe':
                editbar_actions.append(self.bs_subscribe(page))
            elif editbar_item == 'Quicklink':
                editbar_actions.append(self.bs_quicklink(page))
            elif editbar_item == 'Attachments':
                editbar_actions.append(self.bs_attachments(page))
            elif editbar_item == 'ActionsMenu':
                editbar_actions.append(self.bs_actions(page))
        return editbar_actions

    def editbar(self, d):
        page = d['page']
        if not self.shouldShowEditbar(page) or not d['user_valid']:
            return u''

        html = self._cache.get('editbar')
        if html is None:
            # Remove empty items and format as list.
            # The item for showing inline comments is hidden by default.
            # It gets activated through javascript only if inline
            # comments exist on the page.
            items = []
            for item in self.editbarItems(page):
                items.append(item)
            html = u'<small class="pull-right btn-toolbar">%s</small>\n' % ''.join(items)
            self._cache['editbar'] = html

        return html

    def bs_html_stylesheets(self, d):
        """ Assemble html head stylesheet links"""
        leave_str = "charset=\"%s\"" % self.stylesheetsCharset
        html = self.html_stylesheets(d)
        return html.replace(leave_str, "")

    def bs_msg(self, d):
        """  Assemble the msg display """
        msg = self.msg(d)
        if msg != u'':
            return u'''
<div class="alert">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
'''+ msg + '</div>'
        return u''

    def bs_custom_title(self, d):
        title = self.request.getPragma('title')
        if not title:
            if d.has_key('title'):
                title = d['title']
            elif d.has_key('title_text'):
                title = d['title_text']
        return wikiutil.escape(title)

    def bs_container_start(self):
        return u'<div class="container">'

    def bs_container_end(self):
        return u'</div> <!-- // container -->'

    def bs_site_header(self, d):
        try:
            return self.cfg.bs_page_header
        except AttributeError:
            return ''

    def bs_first_header(self):
        try:
            return self.cfg.bs_top_header
        except AttributeError:
            return False

    def bs_page_header(self, d):
        html = []

        html.append('<div class="page-header">')
        if self.bs_first_header():
            if d['page_front_page'] == d['page_name']:
                title = self.request.cfg.sitename
            else:
                title = self.bs_custom_title(d)
            html.append("<h1>%s" % title)
            html.append(self.editbar(d))
            html.append("</h1>")
        else:
            html.append(self.editbar(d))
            html.append('</div>')

        return '\n'.join(html)

    def username(self, d):
        """ Assemble the username / userprefs link

        @param d: parameter dictionary
        @rtype: unicode
        @return: username html
        """
        request = self.request
        _ = request.getText

        userlinks = []
        # Add username/homepage link for registered users. We don't care
        # if it exists, the user can create it.
        if request.user.valid and request.user.name:
            interwiki = wikiutil.getInterwikiHomePage(request)
            name = request.user.name
            aliasname = request.user.aliasname
            if not aliasname:
                aliasname = name
            title = "%s" % aliasname
            # link to (interwiki) user homepage
            homelink = (request.formatter.interwikilink(1, title=title, id="userhome", generated=True, *interwiki) +
                        request.formatter.text(name) +
                        request.formatter.interwikilink(0, title=title, id="userhome", *interwiki))
            userlinks.append(homelink)
            # link to userprefs action
            if 'userprefs' not in self.request.cfg.actions_excluded:
                userlinks.append(d['page'].link_to(request, text=_('Settings'),
                                               querystr={'action': 'userprefs'}, id='userprefs', rel='nofollow'))

        if request.user.valid:
            if request.user.auth_method in request.cfg.auth_can_logout:
                userlinks.append(d['page'].link_to(request, text=_('Logout'),
                                                   querystr={'action': 'logout', 'logout': 'logout'}, id='logout', rel='nofollow'))
        else:
            query = {'action': 'login'}
            # special direct-login link if the auth methods want no input
            if request.cfg.auth_login_inputs == ['special_no_input']:
                query['login'] = '1'
            if request.cfg.auth_have_login:
                userlinks.append(d['page'].link_to(request, text=_("Login"),
                                                   querystr=query, id='login', rel='nofollow'))

        userlinks = [u'<li>%s' % link for link in userlinks]
        links = ' <span class="divider">|</span></li>'.join(userlinks)

        links += "%s" %  request.cfg

        if request.cfg.navi_bar:
            links += ' <span class="divider">|</span></li>'
            userlinks = []

            for text in request.cfg.navi_bar:
                pagename, url = self.splitNavilink(text)
                userlinks.append(url)

            userlinks = [u'<li>%s' % link for link in userlinks]
            links += ' <span class="divider">|</span></li>'.join(userlinks)

        html = u'<ul>%s</li></ul>' % links
        return html

    def bs_breadcrumb(self, d):
        html = [u'<ul class="breadcrumb">']

        try:
            _var = self.cfg.bs_breadcrumb
            for text, url in self.cfg.bs_breadcrumb:
                markup = u'<li><a href="%s">%s</a> <span class="divider">&raquo;</span></li>' % (url, text)
                html.append(markup)
        except AttributeError:
            pass

        if self.request.action not in [u'show', u'', u'refresh']:
            action = self.request.action
        else:
            action = False
        page = wikiutil.getFrontPage(self.request)
        frontpage = page.link_to_raw(self.request, text=self.request.cfg.sitename)
        html.append(u'<li>%s <span class="divider">&raquo;</span></li>' % frontpage)
        segments = d['page_name'].split('/')
        if action:
            segments.append(action)
        curpage = ''
        for s in segments[:-1]:
            curpage += s
            html.append(u'<li>%s  <span class="divider">&raquo;</span></li>' % Page(self.request, curpage).link_to(self.request, s))
            curpage += '/'

        html.append(u'<li class="active">%s</li>' % segments[-1])
        html.append(u'<li class="pull-right">%s</li>' % self.username(d))
        html.append(u'</ul>')
        return '\n'.join(html)

    def bs_footer(self):
        html = []
        html.append(u'<hr><footer>')
        html.append(u'<p class="pull-right"><i class="icon-arrow-up"></i><a href="#">Back to top</a></p>')
        try:
            html.append(self.cfg.bs_page_footer)
        except AttributeError:
            pass
        html.append(u'</footer>')
        return '\n'.join(html)

    def bs_footer_js(self):
        js_files = ('jquery.min.js', 'bootstrap.js')
        html = ''
        for js_file in js_files:
            src = "%s/%s/js/%s" % (self.request.cfg.url_prefix_static, self.name, js_file)
            html += '<script type="text/javascript" src="%s"></script>' % src
        return html

    def bs_html5_magic(self):
        return u'''
<!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
<!--[if lt IE 9]>
<script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
<![endif]-->'''


    def bs_google_analytics(self):
        """ Google Analytics tracking code """
        try:
            _var = self.cfg.bs_ga_prop_id
        except AttributeError:
            return ''

        if self.cfg.bs_ga_prop_id.startswith('UA-'):
            return u'''<script type="text/javascript">

var _gaq = _gaq || [];
_gaq.push(['_setAccount', '%s']);
_gaq.push(['_trackPageview']);

(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

</script>''' % self.cfg.bs_ga_prop_id
        return ''

def execute(request):
    """
    Generate and return a theme object

    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

