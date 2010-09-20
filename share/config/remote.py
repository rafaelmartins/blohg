# -*- coding: utf-8 -*-

import os

REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
THEME = 'bw2col'

LOCALES = {
    'en-us': {
        'name': 'English',
        'locale': 'en_US',
    },
    #'pt-br': {
    #    'name': 'Brazilian Portuguese',
    #    'locale': 'pt_BR',
    #},
}

TITLE = u'Your Title'
TITLE_HTML = u'Your HTML Title'

TAGLINE = {
    'en_US': u'Your tagline.',
    #'pt_BR': u'Sua descrição.',
}

AUTHOR = 'Your Full Name'

# If you want to receive comments in your blog, please create an account
# at http://disqus.com/ and create a comment profile for each locale you
# will support on your blog. After that, put they identifiers below.
DISQUS = {
    #'en_US': '',
    #'pt_BR': '',
}

TIMEZONE = {
    'en_US': 'UTC',
    #'pt_BR': 'America/Sao_Paulo',
}

# If you want to have nice statistics about your visitors, please create
# and Google Analytics account and/or a new website profile. After that,
# put the profile identifier below
#GOOGLE_ANALYTICS = 'UA-2886928-8'

MENU = {
    'en_US': [
        # the 2 itens below are default, please don't remove them, and
	# append the ones you want.
        ('', u'Home'),
        ('post', u'Posts'),
    ],
    #'pt_BR': [
    #    ('', u'Home'),
    #    ('post', u'Posts'),
    #],
}

SIDEBAR = {
    'en_US': [
        (u'Example Sidebar Menu', 'menu', [
            ('http://example.com/', u'Example Link 1'),
            ('http://example.org/', u'Example Link 2'),
            ('http://labs.rafaelmartins.eng.br/', u'Rafael Martins\' labs'),
        ]),
        (u'Example Sidebar Text Block', 'text', u'''\
<p>
    Text paragraph.<br />
    Put what you want here.<br />
    HTML allowed.
</p>
'''),
    ],
    #'pt_BR': [
    #
    #],
}

# If the default tag names created automatically isn't enough for you
# put your replacement here.
TAGS = {
    #'my_tag': u'My TAG',
}
