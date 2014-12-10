#!/usr/bin/python
""" An WMS (gacl) output plugin module for fetch-ban. """

import re
import sys

class FetchBanOutputGACL(object):
    """Reads in a gacl file and a ban list and adds
    the DNs in the ban list to the gacl file.
    Removes all DN that are not in the ban list from the gacl file
    The ban list has been processed elsewhere and is considered clean."""
    # /etc/glite-wms/glite_wms_wmproxy.gacl
    PARAM = "The output file to overwrite"


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
        of the last deny condition"""

        last_deny_at = 0
        first_allow_at = 0

        for i, item in enumerate(gacls):
            if "<allow>" in item:
                first_allow_at = i
                break

        for i, item in enumerate(gacls):
            if "<deny>" in item:
                last_deny_at = i
                if (i-2) < 3:
                    raise ValueError("Unexpected <deny> tag found")


        if last_deny_at > first_allow_at:
            raise ValueError("Unexpected <deny> tag found")

        return last_deny_at

    @staticmethod
    def get_current_naughty_list(gacls):
        """Finds currently banned users"""
        naughty_list = []

        for i, item in enumerate(gacls):
            if "<deny>" in item:
                if (i-2) < 0:
                    # this should be impossible if sanity_check has run
                    raise ValueError("Unexpected <deny> tag found") 
                else:
                    # Extract the DN
                    rnaughty = re.search('<dn>(.*)</dn>', gacls[i-2])
                    # group(0) is the whole string
                    # rnaughty = re.search(r'(<\w+?>)(.*)(</\w+?>)', gacls[i-2])
                    print rnaughty.group(1)
                    naughty_list.append(rnaughty.group(1))
        return naughty_list

    def process(self, ban_list):
        """takes a ban list and adds it to gacl file,
        removes DNs that are not in ban list from the gacl file"""

        # read in current gacl file
        with open(self.__filename) as current_gacl_file:
            gacls = current_gacl_file.read().splitlines()

        # make sure the file looks as expected
        # (<deny> before <allow>)
        try:
            last_deny_at = self.sanity_check(gacls)
        except ValueError as err:
            return str(err)

        naughty_list = self.get_current_naughty_list(gacls)

        if sorted(naughty_list) == sorted(ban_list):
            # print 'nothing to see here, move along'
            pass
        else:
            # rewrite the file with the miscreants in
            newgacls = open(self.__filename, 'w')
            # write the first line and then add the naughty list
            newgacls.write(gacls[0]+'\n')
            for banned in ban_list:

                newgacls.write('  <entry>'+'\n')
                newgacls.write('    <person>\n')
                newgacls.write('      <dn>'+banned+'</dn>\n')
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
                start_here = last_deny_at+4
            for line in gacls[start_here:]:
                newgacls.write(line+'\n')
