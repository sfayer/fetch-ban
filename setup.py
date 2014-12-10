from distutils.core import setup

# fetch-ban installer
setup(name = 'fetch-ban',
      version = '2.0.0',
      description = 'A tool for downloading ban lists',
      scripts = ['fetch-ban'],
      packages = ['FetchBanLib'])

