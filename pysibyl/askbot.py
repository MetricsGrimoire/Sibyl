# Copyright (C) 2014 Bitergia
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
import time

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

import requests

from BeautifulSoup import BeautifulSoup

from pysibyl.db import Base, People, Questions, Tags, QuestionsTags, Answers, Comments
from pysibyl.utils import JSONParser


class QuestionsIter(object):
    """Iterator to go through the set of questions
    """

    def __init__(self, url):
        self.url = url
        self.pages = self._count_q_pages()
        self.current = 1
        self.data = None

    def _count_q_pages(self):
        # count total number of question pages to iterate through
        stream = requests.get(self.url + "/api/v1/questions/?page=1", verify=False)
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        data = parser.data
        pages = int(data.pages)

        return pages

    def __iter__(self):
        return self

    def next(self):
        if self.current > self.pages:
            raise StopIteration
        else:
            questions = self._questions()
            self.current = self.current + 1

            return questions

    def _questions(self):
        # returns next slice of question identifiers
        questions = []  # list of question identifiers

        stream = requests.get(self.url + "/api/v1/questions/?page=" + str(self.current), verify=False)
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        data = parser.data

        for question in data.questions:
            # Each of the question is initialized here
            # Askbot API v1 provides same information when asking
            # for questions in the API, than when asking question by question.
            dbquestion = Questions()
            dbquestion.answer_count = question['answer_count']
            dbquestion.question_identifier = question['id']
            dbquestion.last_activity_by = question['last_activity_by']['id']
            dbquestion.view_count = question['view_count']
            dbquestion.last_activity_at = datetime.datetime.fromtimestamp(int(question['last_activity_at'])).strftime('%Y-%m-%d %H:%M:%S')
            dbquestion.title = question['title']
            dbquestion.url = question['url']
            dbquestion.author_identifier = question['author']['id']
            dbquestion.added_at = datetime.datetime.fromtimestamp(int(question['added_at'])).strftime('%Y-%m-%d %H:%M:%S')
            dbquestion.score = question['score']            

            questions.append(dbquestion)

        return questions



class Askbot(object):
    """Askbot main class
    """

    def __init__(self, url):
        self.url = url
        self.questionHTML = None #Current question working on
        self.alltags = []
        self.allusers =  []

    def questions(self):
        # Iterator through the whole set of questions
        return QuestionsIter(self.url)

    def get_question(self, dbquestion):
        # This function parses extra information only found in the
        # HTML and not throuhg the API v1.

        print "Analyzing: " + dbquestion.url

        # Retrieving information not available through the v1 askbot API
        self.questionHTML = QuestionHTML(dbquestion.url)
        dbquestion.body = self.questionHTML.getBody()

        # Retrieving creation date. Issue found in https://bugs.launchpad.net/openstack-community/+bug/1306558
        # This is a work around, or at least in the following, this will help to double check the creation date
        dbquestion.added_at = self.questionHTML.getDate()

        return dbquestion


    def tags (self, dbquestion):
        tagslist = []
        questiontagslist = []

        tags = self.questionHTML.getTags()
        tagslist, questiontagslist, self.alltags = self.get_tags(dbquestion.question_identifier, tags, self.alltags)

        return tagslist, questiontagslist

    def get_tags(self, question_id, tags, alltags):
        # This function inserts into the questionstags and tags tables
        # information associated to a specific question.
        # This returns an updated version of the tags list

        dbtagslist = []
        dbquestiontagslist = []

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

                dbtagslist.append(dbtag)

                #self.session.add(dbtag)
                #self.session.commit()

            tag_id = alltags.index(tag) + 1

            dbquestiontag = QuestionsTags()
            dbquestiontag.question_identifier = question_id
            dbquestiontag.tag_id = tag_id

            dbquestiontagslist.append(dbquestiontag)

            #self.session.add(dbquestiontag)
            #self.session.commit()

        return dbtagslist, dbquestiontagslist, alltags



    def answers(self, dbquestion):
        # TODO: this does not really return the list of answers
        # of a given dbquestion object. This actually returns
        # the answers that at the point of analysis is in memory
        return self.questionHTML.getAnswers(dbquestion.question_identifier) 


    def question_comments(self, dbquestion):
        # coments associated to that question
        return self.questionHTML.getComments("question", dbquestion.question_identifier)

    def answer_comments(self, dbanswer):
        # comments associated to that answer
        return self.questionHTML.getComments("answer", dbanswer.identifier)

    def get_user(self, user_id):
        stream = requests.get(self.url + "/api/v1/users/" + str(user_id) + "/", verify=False)
        #print(self.url + "/api/v1/users/" + str(user_id) + "/")
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        user = parser.data

        dbuser = People()
        dbuser.username = user['username']
        dbuser.reputation = user['reputation']
        dbuser.avatar = user['avatar']
        dbuser.last_seen_at = datetime.datetime.fromtimestamp(int(user['last_seen_at'])).strftime('%Y-%m-%d %H:%M:%S')
        dbuser.joined_at = datetime.datetime.fromtimestamp(int(user['joined_at'])).strftime('%Y-%m-%d %H:%M:%S')
        dbuser.identifier = user['id']

        return dbuser


class QuestionHTML(Askbot):
    """Question HTML parser.
    """

    def __init__(self, url):
        
        self.url = url
        self.bsoup = BeautifulSoup(requests.get(url, verify=False).text)
        self.tags = []

    def getDate(self):
        # Returns the date of creation of question. 
        # The API is wrongly assigning a date (seems to be random one)
        # More info at: https://bugs.launchpad.net/openstack-community/+bug/1306558
        stats = self.bsoup.findAll(attrs={"class" : re.compile("^box statsWidget")})
        stats = stats[0] # only 1 item in the list

        asked_date = stats.findAll(attrs={"class" : "timeago"})
        asked_date = asked_date[0].text

        return asked_date

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
 
    def getAnswers(self, q_id):
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

            #answer = Answer(identifier, text, date, user_identifier, answer_votes)
            dbanswer = Answers()
            dbanswer.identifier = identifier
            dbanswer.body = text
            dbanswer.user_identifier = user_identifier
            dbanswer.question_identifier = q_id
            dbanswer.submitted_on = date
            dbanswer.votes = answer_votes

            all_answers.append(dbanswer)

        return all_answers

    def getComments(self, typeof, identifier):
        # typeof: "question" or "answer"
        # identifier: question or answer identifier

        div_id = ""
        if typeof == "question":
            div_id = "comments-for-question-" + str(identifier)
        elif typeof == "answer":
            div_id = "comments-for-answer-" + str(identifier)
        else:
            return []

        comments_div = stats = self.bsoup.findAll(attrs={"id" : div_id})
        comments_div = comments_div[0]
     
        comments = comments_div.findAll(attrs={"class" : "comment"})
            
        dbcomments = []
        for comment in comments:
            dbcomment = Comments()

            # question or answer identifier
            if typeof == "question":
                dbcomment.question_identifier = identifier
            if typeof == "answer": 
                dbcomment.answer_identifier = identifier
            # body of comment
            body = comment.findAll(attrs={"class" : "comment-body"})
            body = body[0] #only 1 item in the list
            text = body.text
            dbcomment.body = text
     
            # user identifier
            user = comment.findAll(attrs={"class" : "author"})
            user = user[0]
            href = user['href']
            # link similar to: /en/users/0000/username/ in OpenStack askbot
            user_identifier = href.split('/')[3]
            dbcomment.user_identifier = user_identifier
       
            # time of comment
            comment_date = comment.findAll(attrs={"class" : "timeago"})
            comment_date = comment_date[0].text
            dbcomment.submitted_on = comment_date

            dbcomments.append(dbcomment)

        return dbcomments
