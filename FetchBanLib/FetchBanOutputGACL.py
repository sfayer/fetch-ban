#!/usr/bin/python
""" An WMS (gacl) output plugin module for fetch-ban. """

class FetchBanOutputGACL(object):
  """Reads in a gacl file and replaces the banned DNs."""

  PARAM = "The GACL file to update"

  def __init__(self):
    """ Initialise plugin. """
    self.__filename = None

  def configure(self, filename):
    """ Configure the plugin with the given filename. """
    self.__filename = filename

  @staticmethod
  def sanity_check(gacls):
    """Sanity check of current gacl file.
       Code assumes that <deny> (if any)
       conditions are listed at the beginning of the file.
       If the file looks correct, it returns the line number
       of the last deny condition.
       Raises: ValueError if a problem occurs.
    """

    last_deny_at = 0
    first_allow_at = 0

    for i, item in enumerate(gacls):
      # Find the first allow
      if "<allow>" in item and not first_allow_at:
        first_allow_at = i
      # Find the last deny
      if "<deny>" in item:
        last_deny_at = i
        if (i - 2) < 3:
          # Deny is too close to the top of the file
          raise ValueError("Unexpectedly early <deny> tag found")

    if last_deny_at > first_allow_at:
      # There is a deny after the allow
      raise ValueError("Unexpectedly late <deny> tag found")

    return last_deny_at

  def process(self, ban_list):
    """takes a ban list and adds it to gacl file,
       removes DNs that are not in ban list from the gacl file.
    """

    # read in current gacl file
    try:
      with open(self.__filename) as current_gacl_file:
        gacls = current_gacl_file.read().splitlines()
    except IOError as err:
      return "Failed to read '%s': %s" % (self.__filename, err)

    # make sure the file looks as expected
    # (<deny> before <allow>)
    try:
      last_deny_at = self.sanity_check(gacls)
    except ValueError as err:
      return str(err)

    # rewrite the file with the miscreants in
    try:
      newgacls = open(self.__filename, 'w')
      # write the first line and then add the naughty list
      newgacls.write(gacls[0]+'\n')
      for banned in ban_list:
        newgacls.write('  <entry>\n')
        newgacls.write('    <person>\n')
        newgacls.write('      <dn>' + banned + '</dn>\n')
        newgacls.write('    </person>\n')
        newgacls.write('    <deny>\n')
        newgacls.write('      <exec/>\n')
        newgacls.write('    </deny>\n')
        newgacls.write('  </entry>\n')

      # this is an awful hack, but it'll do for now:
      # the denies are at the beginning of the file,
      # so the starting point would be the forth line after the last deny
      # (if any)
      start_here = 1
      if last_deny_at > 0:
        start_here = last_deny_at + 4
      for line in gacls[start_here:]:
        newgacls.write(line + '\n')

      # Update complete
      newgacls.close()
    except IOError as err:
      return "Failed to write '%s': %s" % (self.__filename, err)
    return None

