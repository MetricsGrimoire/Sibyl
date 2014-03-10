# Copyright (C) 2012-2014 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#    Daniel Izquierdo Cortazar <dizquierdo@bitergia.com>   
#
# Beautiful Soup HTML parser for Askbot QA tool

import requests

from BeautifulSoup import BeautifulSoup


class AskbotHTML(object):
    """Askbot HTML parser
    """

    def __init__(self, url):
        
        self.url = url
        self.html = BeautifulSoup(requests.get(url).text)

    def getBody(self):
        #Returns body question message
    
        bsoup = BeautifulSoup(requests.get(self.url).text)
        metas = bsoup.findAll('meta')

        for meta in metas:
            found = False
            for attr, value in meta.attrs:
                if found:
                    found = False
                    body = value
                if attr == "name" and value == "description":
                    # the following loop of attr, value is the field with the body
                    # of the question
                    found = True

        return unicode(body)


