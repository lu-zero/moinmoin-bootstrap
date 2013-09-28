moinmoin bootstrap theme
------------------------

Theme prepared for wiki.libav.org and wiki.luminem.org, based on
(codereading5)[https://bitbucket.org/speirs/codereading5/].

Instructions
============

Put `bootstrap.py` in your themes directory and `bootstrap` in your
static file directory as usual.

### Configuration

The following configuration items are provided

- bs_page_header
  HTML rendered before the breadcrumb

- bs_breadcrumb
  Additional breadcrumb items to add before the actual breadcrumb
  bs_breadcrumb = ( (u'Display string', 'link URL'), )

- bs_page_footer
  HTML rendered in the <footer> element

- bs_ga_prop_id
  Google analytics id

- bs_top_header
  Set it to true if you want to render the wiki name as initial header

### Patches and custom edits

It is advised to edit PageEditor to use the bootstrap classes, requests
and patches to upstream MoinMoin welcome.

