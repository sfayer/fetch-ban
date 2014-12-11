#!/usr/bin/python
""" Plugin Library for fetch-ban """

# We could do dynamic loading here, but keep it simple for now.

from FetchBanLib.FetchBanInputArgus import FetchBanInputArgus
from FetchBanLib.FetchBanInputStatic import FetchBanInputStatic

INPUTS = {'argus':  FetchBanInputArgus,
          'static': FetchBanInputStatic,
         }

from FetchBanLib.FetchBanOutputDBAN import FetchBanOutputDBAN
from FetchBanLib.FetchBanOutputLCAS import FetchBanOutputLCAS
from FetchBanLib.FetchBanOutputGACL import FetchBanOutputGACL
from FetchBanLib.FetchBanOutputVORM import FetchBanOutputVORM

OUTPUTS = {'dban': FetchBanOutputDBAN,
           'gacl': FetchBanOutputGACL,
           'lcas': FetchBanOutputLCAS,
           'vorm': FetchBanOutputVORM,
          }

