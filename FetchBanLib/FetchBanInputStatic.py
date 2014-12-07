#!/usr/bin/python
""" FetchBanInputStatic - A static file plugin for fetch-ban.
"""

class FetchBanInputStatic(object):
  """A static file (one-DN-per-line) plugin for fetch-ban."""

  PARAM = "Input filename to read from"

  def __init__(self):
    """ Initialise plugin. """
    self.__filename = None
    self.__hostcert = None
    self.__hostkey = None
    self.__ca_path = None

  def configure(self, filename, hostcert, hostkey, ca_path):
    """ Set-up the module. """
    self.__filename = filename
    self.__hostcert = hostcert
    self.__hostkey = hostkey
    self.__ca_path = ca_path

  def process(self):
    """ Get the list of DNs in openssl format from a given file.
        source_url should be a location of a static file on disk.
        The file should contain DNs in openssl format, one per line.
        Each line may optionally be surrounded by " characters.
        Returns: A python list of DN strings.
        Throws an IOError on error.
    """
    dn_list = []
    file_fd = open(self.__filename, "r")
    raw_lines = file_fd.read_lines()
    file_fd.close()
    for line in raw_lines:
      line = line.strip()
      if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
      if line.startswith("#"):
        continue # Ignore comments
      dn_list.append(line)
    return dn_list

