#!/usr/bin/python

import os
import sys
import time
import pickle
import pycurl
import random
import StringIO
from xml.dom import minidom

# A list of tuples, each tuple should be (PAP Host, List alias)
PAP_LIST = [('https://argusngi.gridpp.rl.ac.uk:8150', 'default')]
# The endpoint to suffix on all of the ARGUS urls
PAP_ENDPOINT = '/pap/services/XACMLPolicyManagementService'
# The max random delay to wait before fetching the ban list (seconds)
MAX_DELAY = 360
# Set this to true to print when a DN is added or removed to STDOUT
AUDIT_CHANGES = True
# The standard hostcert, hostkey & CA dir settings
HOSTCERT = '/etc/grid-security/hostcert.pem'
HOSTKEY = '/etc/grid-security/hostkey.pem'
CADIR = '/etc/grid-security/certificates'
# Output and state settings
OUTPUT_FILE = '/etc/lcas/ban_users.db'
STATIC_FILE = '/etc/lcas/ban_static.db'
STATE_FILE = '/etc/lcas/ban_users.pkl'

# The XML request we send (containing one %s for the alias)
XML_REQ = \
"""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns0="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://services.pap.authz.glite.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<SOAP-ENV:Header/>
  <ns1:Body><ns2:listPolicies><papAlias>%s</papAlias></ns2:listPolicies></ns1:Body>
</SOAP-ENV:Envelope>
"""


def rfc_to_openssl(dn):
  """ Converts an RFC2253 DN string into an openssl one. """
  dn_parts = [x.strip() for x in dn.split(',')]
  dn_parts.reverse()
  return '/%s' % '/'.join(dn_parts)


def fetch_ban_list(url, alias):
  """ Get the list of DNs in openssl format from a given URL.
      Returns: A python list of DN strings.
  """
  dn_list = []
  # Post the request to get the ban list (in XML format)
  curl = pycurl.Curl()
  curl.setopt(curl.URL, url)
  data = XML_REQ % alias
  curl.setopt(curl.POSTFIELDS, data)
  curl.setopt(curl.CAPATH, CADIR)
  curl.setopt(curl.SSLCERT, HOSTCERT)
  curl.setopt(curl.SSLKEY, HOSTKEY)
  curl.setopt(curl.HTTPHEADER, ['SOAPAction: ""'])
  body = StringIO.StringIO()
  curl.setopt(curl.WRITEFUNCTION, body.write)
  curl.perform()
  code = curl.getinfo(pycurl.HTTP_CODE)
  if code != 200:
    raise Exception("Failed to query '%s' for '%s' (Code: %d)" % \
                      (url, alias, code))
  # We now have the XML doc in body.getvalue(), decode it
  doc = minidom.parseString(body.getvalue())
  for rule in doc.getElementsByTagName('xacml:Rule'):
    # Find out only the ban rules
    if rule.getAttribute('Effect').lower() == 'deny':
      # Get all of the subjects out of the list
      for subjectm in rule.getElementsByTagName('xacml:SubjectMatch'):
        # Get the two parts of the subject (there should only be one of each)
        subject_ad = subjectm.getElementsByTagName('xacml:SubjectAttributeDesignator')[0]
        subject = subjectm.getElementsByTagName('xacml:AttributeValue')[0]
        if subject_ad.getAttribute('AttributeId').lower() != \
             'urn:oasis:names:tc:xacml:1.0:subject:subject-id':
          continue # Skip things that aren't DNs
        dn = subject.firstChild.nodeValue
        dn_list.append(rfc_to_openssl(dn))
  return dn_list


if __name__ == '__main__':
  # Load the previous bans if they exist
  prev_bans = {}
  if os.path.exists(STATE_FILE):
    fd = open(STATE_FILE, 'r')
    prev_bans = pickle.load(fd)
    fd.close()
  # Wait for a random delay
  time.sleep(random.randint(1, MAX_DELAY))
  # Loop over all of the ARGUS PAP servers & aliases
  bans = {}
  for ruleset in PAP_LIST:
    url = '%s%s' % (ruleset[0], PAP_ENDPOINT)
    key = '%s-%s' % (url, ruleset[1])
    try:
      bans[key] = fetch_ban_list(url, ruleset[1])
    except Exception, err:
      print "Error fetching ban list: %s" % str(err)
      # Fetching the bans failed, use the old list if there was one...
      if key in prev_bans:
        bans[key] = prev_bans[key]
      continue
    # Compare the old and new lists (if the old list exists) and print out
    # any changes if that feature is enabled...
    if AUDIT_CHANGES:
      if key in prev_bans:
        before = set(prev_bans[key])
      else:
        before = set()
      after = set(bans[key])
      for del_user in before - after:
        print "Unbanned DN: %s" % del_user
      for add_user in after - before:
        print "Banned DN: %s" % add_user

  # Create the full ban list (static file + dynamic entries)
  dn_list = []
  if os.path.exists(STATIC_FILE):
    fd = open(STATIC_FILE, 'r')
    for dn in fd.readlines():
      dn_list.append(dn.strip())
    fd.close()
  # Add dynamic entries
  for key in bans:
    for dn in bans[key]:
      dn_list.append('"%s"' % dn)
  # Remove duplicates and output
  fd = open(OUTPUT_FILE, 'w')
  for dn in set(dn_list):
    fd.write('%s\n' % dn)
  fd.close()
  # Output our state file too
  fd = open(STATE_FILE, 'w')
  pickle.dump(bans, fd)
  fd.close()
  # Everything done
  sys.exit(0)

