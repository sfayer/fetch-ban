#!/usr/bin/python
""" FetchBanInputArgus - An ARGUS plugin for fetch-ban.
"""

import pycurl
import StringIO
from xml.dom import minidom


class FetchBanInputArgus(object):
  """An ARGUS client plugin for fetch-ban."""

  PARAM = "Argus URL in URL#alias format"

  # The XML request we send (containing one %s for the alias)
  __XML_REQ = \
  """<?xml version="1.0" encoding="UTF-8"?>
     <SOAP-ENV:Envelope
        xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
        xmlns:ns0="http://schemas.xmlsoap.org/soap/encoding/"
        xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns2="http://services.pap.authz.glite.org"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
        SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
         <SOAP-ENV:Header/>
         <ns1:Body>
           <ns2:listPolicies><papAlias>%s</papAlias></ns2:listPolicies>
         </ns1:Body>
     </SOAP-ENV:Envelope>
  """

  @staticmethod
  def __rfc_to_openssl(user_dn):
    """ Converts an RFC2253 DN string into an openssl one. """
    dn_parts = [x.strip() for x in user_dn.split(',')]
    dn_parts.reverse()
    return '/%s' % '/'.join(dn_parts)

  def __init__(self):
    """ Initialise plugin. """
    self.__url = None
    self.__alias = None
    self.__hostcert = None
    self.__hostkey = None
    self.__ca_path = None

  def configure(self, source_url, hostcert, hostkey, ca_path):
    """ Configure the plugin.
        Returns None on success or an error string otherwise.
    """
    try:
      self.__url, self.__alias = source_url.split("#")
    except ValueError:
      return "Failed to parse URL#alias notation"
    self.__hostcert = hostcert
    self.__hostkey = hostkey
    self.__ca_path = ca_path

  def process(self):
    """ Get the list of DNs in openssl format from a given URL.
        source_url should be an ARGUS endpoint https:// URL, the
        policy alias should be appended with a hash to the end of the URL:
        https://my.argus/endpoint#Alias
        ca_path, hostcert & hostkey are the paths to the CA certificates path,
        the hostcert PEM and hostkey PEM files respectively.
        Returns: A python list of DN strings.
        Throws an IOError on error.
    """
    dn_list = []
    # Post the request to get the ban list (in XML format)
    curl = pycurl.Curl()
    curl.setopt(curl.URL, self.__url)
    data = self.__XML_REQ % self.__alias
    curl.setopt(curl.POSTFIELDS, data)
    curl.setopt(curl.CAPATH, self.__ca_path)
    curl.setopt(curl.SSLCERT, self.__hostcert)
    curl.setopt(curl.SSLKEY, self.__hostkey)
    curl.setopt(curl.HTTPHEADER, ['SOAPAction: ""'])
    body = StringIO.StringIO()
    curl.setopt(curl.WRITEFUNCTION, body.write)
    try:
      curl.perform()
    except pycurl.error as err:
      raise IOError("Failed to query ARGUS '%s' for '%s': %s" % \
                     (self.__url, self.__alias, err[1]))
    code = curl.getinfo(pycurl.HTTP_CODE)
    if code != 200:
      raise IOError("Failed to query ARGUS '%s' for '%s' (Code: %d)" % \
                     (self.__url, self.__alias, code))
    # We now have the XML doc in body.getvalue(), decode it
    doc = minidom.parseString(body.getvalue())
    for rule in doc.getElementsByTagName('xacml:Rule'):
      # Find out only the ban rules
      if rule.getAttribute('Effect').lower() == 'deny':
        # Get all of the subjects out of the list
        for match in rule.getElementsByTagName('xacml:SubjectMatch'):
          # Get the two parts of the subject (there should only be one of each)
          subject_ad = \
            match.getElementsByTagName('xacml:SubjectAttributeDesignator')[0]
          subject = match.getElementsByTagName('xacml:AttributeValue')[0]
          if subject_ad.getAttribute('AttributeId').lower() != \
               'urn:oasis:names:tc:xacml:1.0:subject:subject-id':
            continue # Skip things that aren't DNs
          user_dn = subject.firstChild.nodeValue
          dn_list.append(self.__rfc_to_openssl(user_dn))
    return dn_list

