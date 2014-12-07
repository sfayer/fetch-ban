#!/usr/bin/python
""" An LCAS output plugin module for fetch-ban. """


class FetchBanOutputLCAS(object):
  """Write to an LCAS-style ban_user.db file."""

  PARAM = "The output file to overwrite"

  def __init__(self):
    """ Initialise plugin. """
    self.__filename = None

  def configure(self, filename):
    """ Configure the plugin with the given filename. """
    self.__filename = filename

  def process(self, ban_list):
    """ Overwrite filename with the list of DNs.
        Each DN will be on a seperate line and surrounded by
        double quotes.
    """
    try:
      file_fd = open(self.__filename, "w")
      for user_dn in ban_list:
        file_fd.write('"%s"\n' % user_dn)
      file_fd.close()
    except IOError as err:
      return "Failed to write file '%s': %s" % (self.__filename, err)
    return # All OK

