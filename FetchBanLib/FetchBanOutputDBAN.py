#!/usr/bin/python
""" A dCache ban.conf output plugin module for fetch-ban.
"""

# Base file text
BASE_TEXT = "### This file will be overwritten by fetch-ban.\n" \
            "alias dn=org.globus.gsi.jaas.GlobusPrincipal\n\n"
# Template for DN
DN_TEXT = "ban dn:%s\n"

class FetchBanOutputDBAN(object):
  """Overwrite a dCache ban.conf file."""

  PARAM = "The output file to overwrite"

  def __init__(self):
    """ Initialise plugin. """
    self.__filename = None

  def configure(self, filename):
    """ Configure the plugin with the given filename. """
    self.__filename = filename

  def process(self, ban_list):
    """ Overwrite the ban.conf file with the updated DN list.
    """
    # Re-write the file
    try:
      file_fd = open(self.__filename, "w")
      file_fd.write(BASE_TEXT)
      for ban_dn in ban_list:
        file_fd.write(DN_TEXT % ban_dn)
      file_fd.close()
    except IOError as err:
      return "Failed to write file '%s': %s" % (self.__filename, err)
    return # All OK

