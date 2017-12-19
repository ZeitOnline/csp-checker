name             'zeit-csp-checker'
version          '0.1.0'

maintainer       'Zeit Online GmbH'
maintainer_email 'Zeit Backend Team <zon-backend@zeit.de>'
issues_url       nil
source_url       nil
license          'All rights reserved'
description      'Checks the Content Security Policy with ELK'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))

chef_version     '>= 12'
supports         'ubuntu', '>= 16.04'

depends          "apt"
depends          "chef-sugar"
