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
#    Alvaro del Castillo <acs@bitergia.com>   
#
# Beautiful Soup HTML parser for Discourse QA tool

from dateutil.parser import parse
import datetime
import logging
import re
import requests

from pysibyl.db import People, Questions, Tags, QuestionsTags, Answers, Comments
from pysibyl.utils import JSONParser


class QuestionsDiscourse(object):
    """Iterator to go through the set of questions
    """

    def __init__(self, url, category):
        self.url = url
        self.data = None
        self.category = category

    def questions(self):
        questions = []

        url = self.url + "/c/" + self.category + ".json"
        stream = requests.get(url, verify=False)
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        data = parser.data
        data = data['topic_list']['topics']

        for question in data:
            # Each of the question is initialized here
            dbquestion = Questions()
            for poster in question['posters']:
                if poster['description'] == 'Original Poster':
                    dbquestion.author_identifier = poster['user_id']
                elif poster['description'] == 'Most Recent Poster':
                    dbquestion.last_activity_by = poster['user_id']

            dbquestion.answer_count = question['posts_count']
            dbquestion.question_identifier = question['id']
            dbquestion.view_count = question['views']
            if question['last_posted_at'] is not None:
                dbquestion.last_activity_at = parse(question['last_posted_at']).strftime('%Y-%m-%d %H:%M:%S')
            else:
                dbquestion.last_activity_at = parse(question['created_at']).strftime('%Y-%m-%d %H:%M:%S')
            dbquestion.title = question['title']
            dbquestion.title = question['body']
            dbquestion.url = self.url +"/t/"+question['slug']
            dbquestion.added_at = parse(question['created_at']).strftime('%Y-%m-%d %H:%M:%S')
            # dbquestion.score = question['score']

            questions.append(dbquestion)

        return questions

class Discourse(object):
    """Discourse main class
    """

    def __init__(self, url):
        self.url = url
        self.questionHTML = None #Current question working on
        self.alltags = []
        self.allusers =  []

    def questions(self, category):
        return QuestionsDiscourse(self.url, category).questions()

    def remove_question(self, dbquestion, session):
        # This function removes all information in cascade for
        # info found in dbquestion. Given that we're using Myisam
        # the cascade removal is manually done.

        # removing question
        query_question = session.query(Questions).\
            filter(Questions.question_identifier==int(dbquestion.question_identifier))
        question = query_question.first()
        session.delete(question)

        # removing tags
        query_tags = session.query(QuestionsTags).\
            filter(QuestionsTags.question_identifier==int(dbquestion.question_identifier))
        tags = query_tags.all()
        for tag in tags:
            session.delete(tag)

        # removing comments
        query_comments = session.query(Comments).\
            filter(Comments.question_identifier==int(dbquestion.question_identifier))
        comments = query_comments.all()
        for comment in comments:
            session.delete(comment)

        # removing answers and their comments
        query_answers = session.query(Answers).\
            filter(Answers.question_identifier==int(dbquestion.question_identifier))
        answers = query_answers.all()
        answer_id = 0
        for answer in answers:
            answer_id = answer.identifier
            session.delete(answer)
            query_comments = session.query(Comments).\
                filter(Comments.answer_identifier==int(answer_id))
            comments = query_comments.all()
            for comment in comments:
                session.delete(comment)
        session.commit()

    def is_question_updated(self, dbquestion, session):
        # This function checks if the dbquestion is updated
        # according to the information found in the database
        # and the "last_activity_at" field

        updated = True
        found = True

        query_question = session.query(Questions).\
            filter(Questions.question_identifier==int(dbquestion.question_identifier))
        questions = query_question.all()

        if len(questions) == 0:
            #question not found in db
            logging.info( "    * Question not found in db")
            found = False
            updated = False

        else:
            # question in db
            question = questions[0]
            # question data from API
            date = datetime.datetime.strptime(dbquestion.last_activity_at, "%Y-%m-%d %H:%M:%S")
            if question.last_activity_at < date:
                #question not updated in db
                logging.info("    * Question not updated in db")
                updated = False

        return updated, found

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
        logging.info(stream.url)
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

    def categories(self):
        stream = requests.get(self.url + "/categories.json", verify=False)
        logging.info(stream.url)
        #print(self.url + "/api/v1/users/" + str(user_id) + "/")
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        categories = parser.data['category_list']['categories']

        return categories




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

            m = re.match(self.USER_HREF_REGEXP, href)
            user_identifier = m.group(1)

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

        comments_div = self.bsoup.findAll(attrs={"id" : div_id})
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

            m = re.match(self.USER_HREF_REGEXP, href)
            user_identifier =  m.group(1)
            dbcomment.user_identifier = user_identifier

            # time of comment
            comment_date = comment.findAll(attrs={"class" : "timeago"})
            comment_date = comment_date[0].text
            dbcomment.submitted_on = comment_date

            dbcomments.append(dbcomment)

        return dbcomments
