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

import re

import requests

from BeautifulSoup import BeautifulSoup

class Answer(object):
    """Askbot Answer basic class
    """

    def __init__(self, identifier, body, date, user, votes):
      
        self.identifier = identifier
        self.body = body
        self.date = date
        self.user_identifier = user
        self.votes = votes


class AskbotQuestionHTML(object):
    """Askbot Question HTML parser.
    """

    def __init__(self, url):
        
        self.url = url
        self.bsoup = BeautifulSoup(requests.get(url).text)
        self.tags = []

    def getBody(self):
        # Returns body question message
        # This is found under the <meta name="description" content="">
    
        metas = self.bsoup.findAll('meta')
        body = ""

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

    def getTags(self):
        # Returns a list of tags
        # This is found under the <meta name="keywords" content="">
        # Keywords are comma separated
        
        metas = self.bsoup.findAll('meta')
        tags = ""

        for meta in metas:
            found = False
            for attr, value in meta.attrs:
                if found:
                    found = False
                    tags = value
                if attr == "name" and value == "keywords":
                    # the following loop of attr, value is the field with the body
                    # of the question
                    found = True

        return tags.split(',')
 
    def getAnswers(self):
        # Returns a list of answers with their comments if exist

        answers = self.bsoup.findAll(attrs={"class" : re.compile("^post answer")})

        all_answers = []
        for answer in answers:
            # Obtain body of the message
            body = answer.findAll(attrs={"class" : "post-body"})
            body = body[0] #only 1 item in the list
            text = body.text

            # Obtain unique askbot identifier
            identifier = int(answer.attrMap['data-post-id'])

            # Obtain time of the answer
            date_tag = answer.findAll('abbr')
            date = date_tag[0].text 

            # Obtain user card
            user = answer.findAll(attrs={"class" : "user-card"})
            # User name is obtain from the text of the second <a> tag
            user_links = user[0].findAll('a')
            user_name = user_links[1].text
            link = user_links[1]
            href = link['href']
            # link similar to: /en/users/0000/username/ in OpenStack askbot
            user_identifier = href.split('/')[3]

            # Obtain votes 
            votes = answer.findAll(attrs={"class" : "vote-number"})
            answer_votes = int(votes[0].text)

            answer = Answer(identifier, text, date, user_identifier, answer_votes)
            all_answers.append(answer)

        return all_answers

