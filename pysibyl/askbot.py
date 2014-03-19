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
import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

import requests

from BeautifulSoup import BeautifulSoup

from pysibyl.db import Base, People, Questions, Tags, QuestionsTags, Answers
from pysibyl.utils import JSONParser


class Askbot(object):
    """Askbot JSON and HTML parser
    """

    def __init__(self, session, url):
        # Initial constructor
        self.session = session
        self.url = url
        self.info = None
        self.questions = None

    def parser(self):
        # Initial parsing of general info, users and questions

        self.info = self.general_info()
        #self.users()
        self.questions = self.askbot_questions()

    def general_info(self):
        # Expected basic info: total users, total pages, total questions

        stream = requests.get(self.url + "/api/v1/info/")
        parser = JSONParser(unicode(stream.text))
        parser.parse()

        return parser.data


    def users(self):
        # Parsing users through the API

        cont = 1
        pages = 1
        while cont <= pages:
            stream = requests.get(self.url + "/api/v1/users/?page=" + str(cont))
            cont = cont + 1
            parser = JSONParser(unicode(stream.text))
            parser.parse()
            data = parser.data
            pages = int(data.pages)
 
            for user in data.users:
                dbuser = People()
                dbuser.username = user['username']
                dbuser.reputation = user['reputation']
                dbuser.avatar = user['avatar']
                dbuser.last_seen_at = datetime.datetime.fromtimestamp(int(user['last_seen_at'])).strftime('%Y-%m-%d %H:%M:%S')
                dbuser.joined_at = datetime.datetime.fromtimestamp(int(user['joined_at'])).strftime('%Y-%m-%d %H:%M:%S')
                dbuser.identifier = user['id']

                self.session.add(dbuser)
                self.session.commit()

        return users


    def askbot_questions(self):
        # For each question, answers are retrieved.
        # This is a mix of API + HTML parser

        cont = 1
        pages = 1
        alltags = []
        while cont <= pages:
            print "Analyzing: " + self.url + "/api/v1/questions/?page=" + str(cont)
            stream = requests.get(self.url + "/api/v1/questions/?page=" + str(cont))
            cont = cont + 1
            parser = JSONParser(unicode(stream.text))
            parser.parse()
            data = parser.data
            pages = int(data.pages)

            for question in data.questions:
                print "Analyzing: " + question['url']

                dbquestion = Questions()
                dbquestion.answer_count = question['answer_count']
                dbquestion.question_identifier = question['id']
                dbquestion.last_activity_by = question['last_activity_by']['id']
                dbquestion.view_count = question['view_count']
                dbquestion.last_activity_at = datetime.datetime.fromtimestamp(int(question['last_activity_at'])).strftime('%Y-%m-%d %H:%M:%S')
                dbquestion.title = question['title']
                dbquestion.url = question['url']
                dbquestion.author = question['author']['id']
                dbquestion.added_at = datetime.datetime.fromtimestamp(int(question['added_at'])).strftime('%Y-%m-%d %H:%M:%S')
                dbquestion.score = question['score']

                # Retrieving information not available through the v1 askbot API
                askbot = AskbotQuestionHTML(question['url'])
                dbquestion.body = askbot.getBody()
                tags = askbot.getTags()
                alltags = self.askbot_tags(question['id'], tags, alltags)
                answers = askbot.getAnswers()
                self.askbot_answers(answers, question['id'])

                self.session.add(dbquestion)
                self.session.commit()


    def askbot_answers(self, answers, question_identifier):
        # Insert in database all of the answers related to question_id

        for answer in answers:
            dbanswer = Answers()
            dbanswer.body = answer.body
            dbanswer.submitted_on = answer.date
            dbanswer.question_identifier = question_identifier
            dbanswer.votes = answer.votes
            dbanswer.identifier = answer.identifier
            dbanswer.user_identifier = answer.user_identifier
            self.session.add(dbanswer)
            self.session.commit()

    def askbot_tags(self, question_id, tags, alltags):
        # This function inserts into the questionstags and tags tables
        # information associated to a specific question.
        # This returns an updated version of the tags list

        for tag in tags:
            if tag not in alltags:
                # new tag found
                # WARNING: in case this tool is modified to be incremental,
                # this will fail. This is due to the tags list structure is
                # started from scratch and not initialize based on db existing data
                alltags.append(tag)
                # insert tag in db
                dbtag = Tags()
                dbtag.tag = tag

                self.session.add(dbtag)
                self.session.commit()

            tag_id = alltags.index(tag) + 1

            dbquestiontag = QuestionsTags()
            dbquestiontag.question_identifier = question_id
            dbquestiontag.tag_id = tag_id

            self.session.add(dbquestiontag)
            self.session.commit()

        return alltags




class Answer(Askbot):
    """Askbot Answer basic class
    """

    def __init__(self, identifier, body, date, user, votes):
      
        self.identifier = identifier
        self.body = body
        self.date = date
        self.user_identifier = user
        self.votes = votes


class AskbotQuestionHTML(Askbot):
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

