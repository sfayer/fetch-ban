#!/usr/bin/python
""" An vo-rolemap output plugin module for fetch-ban.
    This is suitable for banning on dCache.
"""

# The username to use for the banned users
BANNED_USERNAME = "-"
# The guard header text
GUARD_TEXT = "### This block was automatically added by fetch-ban.\n" \
             "### Please do not edit it by hand."
GUARD_START = "### fetch-ban start"
GUARD_END = "### fetch-ban end"

class FetchBanOutputVORM(object):
  """Write to a grid-vorolemap file."""

  PARAM = "The output file to update"

  def __init__(self):
    """ Initialise plugin. """
    self.__filename = None

  def configure(self, filename):
    """ Configure the plugin with the given filename. """
    self.__filename = filename

  def process(self, ban_list):
    """ Update the vo-rolemap file.
        The banned DNs are added in "/some/dn" "" "BANNED_USERNAME" format,
        one per line where BANNED_USERNAME is the provided constant.
        These entries will be put in a special section marked clearly as
        being for fetch-ban. If this section doesn't exist, it will be
        created at the start of the file.
    """
    # Load the original file
    vorm_lines = []
    try:
      file_fd = open(self.__filename, "r")
      vorm_lines = file_fd.readlines()
      file_fd.close()
    except IOError as err:
      return "Failed to read file '%s': %s" % (self.__filename, err)
    # Update the ban list
    ## Find the guard lines
    guard_start = -1
    guard_end = -1
    for i, line_text in enumerate(vorm_lines):
      if line_text.startswith(GUARD_START):
        # We want to do operations on the line _after_ the start guard
        guard_start = i + 1
      elif line_text.startswith(GUARD_END):
        guard_end = i
        break
    # Catch various special conditions
    # We don't need to catch guard_start after guard_end as the previous
    # loop stops when it sees the end (so guard_start will be -1)
    if guard_start < 0 and guard_end < 0:
      # The guard block is missing, add it
      vorm_lines.insert(0, "%s\n" % GUARD_TEXT)
      vorm_lines.insert(1, "%s\n" % GUARD_START)
      vorm_lines.insert(2, "%s\n\n" % GUARD_END)
      guard_start = 2
      guard_end = 2
    elif guard_start < 0:
      return "Unmatched end guard found?"
    elif guard_end < 0:
      return "Unmatched start guard found?"
    ## Erase the existing lines
    del vorm_lines[guard_start:guard_end]
    ## Add the bans
    for i, ban_dn in enumerate(ban_list):
      vorm_lines.insert(guard_start, '"%s" "" %s\n' % \
                                       (ban_dn, BANNED_USERNAME))
    # Re-write the file
    try:
      file_fd = open(self.__filename, "w")
      for file_line in vorm_lines:
        file_fd.write(file_line)
      file_fd.close()
    except IOError as err:
      return "Failed to write file '%s': %s" % (self.__filename, err)
    return # All OK

