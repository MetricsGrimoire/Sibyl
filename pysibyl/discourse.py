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
# Sibyl backend for Discourse QA tool

import datetime
import logging
import requests

from pysibyl.db import People, Questions, Tags, QuestionsTags, Answers, Comments
from pysibyl.utils import JSONParser


class Discourse(object):
    """Discourse main class
    """

    def __init__(self, url, session):
        self.url = url
        self.questionHTML = None #Current question working on
        self.alltags = []
        self.allusers =  []
        self.debug = False
        self.dbtags = []
        self.session = session
        self.pagesize = 100 # max for stacjoverflow
        self.api_limit = 10000 # max default
        self.api_queries = 0
        self.user_ids_questions = []
        self.user_ids_answers = []
        self.users_blacklist = []
        self.total_users = 0
        self.total_questions = 0
        self.total_answers = 0
        self.total_comments = 0

    def process_questions(self, category):
        logging.debug("Processing questions for " + category)

        def update_users(users):
            for user in users:
                if user['username'] not in self.user_ids_questions:
                    self.user_ids_questions.append(user['username'])

        def process_question(question):
            dbquestion = Questions()
            dbquestion.author_identifier = question['posters'][0]['user_id']
            dbquestion.answer_count = question['reply_count']
            dbquestion.question_identifier = question['id']
            dbquestion.view_count = question['views']
            if question['last_posted_at'] is not None:
                dbquestion.last_activity_at = question['last_posted_at']
            else:
                dbquestion.last_activity_at = question['created_at']
            dbquestion.title = question['title']
            dbquestion.url = question['slug']
            dbquestion.added_at = question['created_at']
            dbquestion.score = question['like_count']
            # dbquestion.last_activity_by = question['last_poster_username']
            dbquestion.body = None
            if 'excerpt' in question:
                dbquestion.body = question['excerpt']
            # Additional fields in Discourse: liked,pinned_globally, visible, highest_post_number, unseen,posts_count
            # bumped_at, bookmarked, archived,archetype,has_summary,pinned,image_url,closed,unpinned,bumped, fancy_title

            if self.question_new_or_changed(dbquestion):
                # Question is new or changed
                self.session.add(dbquestion)
                self.session.commit()
                self.process_answers(question['slug'])
                self.process_dbquestiontags(dbquestion.question_identifier, category)
                update_users = False
            self.total_questions += 1


        url = self.url + "/c/" + category + ".json"
        stream = requests.get(url, verify=False)
        print url
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        data = parser.data

        data = data['topic_list']['topics']

        for question in data:
            process_question(question)
        update_users(parser.data['users'])
        self.process_users(self.user_ids_questions)

        while 'more_topics_url' in parser.data['topic_list']:
            url = self.url + parser.data['topic_list']['more_topics_url']
            print url
            stream = requests.get(url, verify=False)
            parser = JSONParser(unicode(stream.text))
            parser.parse()
            data = parser.data

            data = data['topic_list']['topics']

            for question in data:
                process_question(question)
            if 'users' in parser.data:
                update_users(parser.data['users'])
                self.process_users(self.user_ids_questions)
            else:
                logging.info("Questions without users")
                print (parser.data)
        return

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

    def question_new_or_changed(self, dbquestion):
        question_changed = True

        updated, found = self.is_question_updated(dbquestion, self.session)
        if found and updated:
            # no changes needed
            logging.debug ("    * NOT updating information for this question")
            question_changed = False

        if found and not updated:
            # So far using the simpliest approach: remove all info related to
            # this question and re-insert values: drop question, tags,
            # answers and comments for question and answers.
            # This is done in this way to avoid several 'if' clauses to
            # control if question was found/not found or updated/not updated
            logging.debug ("Restarting dataset for this question")
            self.remove_question(dbquestion, self.session)

        return question_changed

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
            logging.debug( "    * Question not found in db")
            found = False
            updated = False

        else:
            # question in db
            question = questions[0]
            # question data from API
            # 2014-06-25T20:29:21.510Z
            date = datetime.datetime.strptime(dbquestion.last_activity_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            date = date.replace(microsecond=0) # microsecs not stored in mysql
            if question.last_activity_at < date:
                #question not updated in db
                logging.debug("    * Question not updated in db")
                updated = False

        return updated, found

    def categories(self):
        stream = requests.get(self.url + "/categories.json", verify=False)
        logging.info(stream.url)
        #print(self.url + "/api/v1/users/" + str(user_id) + "/")
        parser = JSONParser(unicode(stream.text))
        parser.parse()
        categories = parser.data['category_list']['categories']
        return categories

    def process_dbquestiontags(self, question_identifier, tag):
        dbquestiontag = QuestionsTags()
        dbquestiontag.question_identifier = question_identifier
        for dbtag in self.dbtags:
            if dbtag.tag == tag:
                dbquestiontag.tag_id = dbtag.id
                break
        if dbquestiontag.tag_id is None:
            logging.debug(tag + " NOT found. Adding it")
            # First look for it in the db
            dbtag = self.session.query(Tags).filter(Tags.tag == tag).first()
            if dbtag is None:
                dbtag = Tags()
                dbtag.tag = tag
                self.session.add(dbtag)
                self.session.commit()
            self.dbtags.append(dbtag)
            dbquestiontag.tag_id = dbtag.id

        self.session.add(dbquestiontag)
        self.session.commit()
 
    def process_answers(self, question_slug):
        """ Get all answers for the question with slug dbquestion_slug  """

        def process_answer(answer):
            dbanswer = Answers()
            dbanswer.identifier = answer['id']
            # dbanswer.body = text
            dbanswer.user_identifier = answer['user_id']
            if answer['username'] not in self.user_ids_answers:
                self.user_ids_answers.append(answer['username'])
            dbanswer.question_identifier = question_id
            dbanswer.submitted_on = answer['updated_at']
            dbanswer.votes = answer['score']
            dbanswer.body = answer['cooked']

            self.session.add(dbanswer)
            self.total_answers += 1


        url = self.url + "/t/" + question_slug + ".json"
        logging.info("Getting answers for " + question_slug)
        logging.info(url)
        stream = requests.get(url, verify=False)
        parser = JSONParser(unicode(stream.text))
        try:
            parser.parse()
        except:
            logging.error("Cant parse answers for question " + question_slug)
            print unicode(stream.text)
            return

        data = parser.data

        question_id = parser.data['id']
        data = data['post_stream']['posts']

        for answer in data:
            process_answer(answer)
        self.session.commit()
        self.process_users(self.user_ids_answers)

        # It there are more than 20 answers we need to retrieve the rest
        discoure_max_answers_query = 20

        if len(parser.data['post_stream']['stream']) > 20:
            pending = parser.data['post_stream']['stream']
            for i in range(0,discoure_max_answers_query): pending.pop(0)
            url = self.url + "/t/"+ str(question_id) + "/posts.json?"
            for answer_id in pending:
                url += "post_ids%5B%5D="+str(answer_id)+"&"
            stream = requests.get(url, verify=False)
            parser = JSONParser(unicode(stream.text))
            try:
                parser.parse()
            except:
                logging.error("Cant parse additional answers for question " + question_slug)
                logging.error(url)
                print unicode(stream.text)
                return

            data = parser.data

            data = data['post_stream']['posts']

            for answer in data:
                process_answer(answer)
            self.session.commit()
            self.process_users(self.user_ids_answers)

    def process_users(self, users_ids):
        if users_ids is None: return

        for user_id in users_ids:
            if user_id in self.users_blacklist: continue
            user = self.session.query(People).filter(People.username == user_id).first()
            if user is not None: continue

            url = self.url + "/users/" + user_id + ".json"
            logging.info("Getting user " + user_id)
            logging.info(url)
            stream = requests.get(url, verify=False)
            try:
                parser = JSONParser(unicode(stream.text))
                parser.parse()
            except:
                logging.error("Can't get " + user_id + " data")
                self.users_blacklist.append(user_id)
                # print unicode(stream.text)
                continue

            user = parser.data['user']

            dbuser = People()
            dbuser.username = user['username']
            dbuser.reputation = user['trust_level']
            dbuser.avatar = user['uploaded_avatar_id']
            dbuser.last_seen_at = user['last_posted_at']
            dbuser.joined_at = user['created_at']
            dbuser.identifier = user['id']
            self.session.add(dbuser)
            self.total_users += 1
        self.session.commit()

        return


    def parse(self):
        # Initial parsing of general info, users and questions
        for category in  self.categories():
            logging.info("Parsing category: " + category['slug'])
            self.process_questions(category['slug'])
        self.report()

    def report(self):
        print "Total number of users added " + str(self.total_users)
        print "Total number of questions checked " + str(self.total_questions)
        print "Total number of answers added " + str(self.total_answers)
        print "Users not found: "
        print self.users_blacklist
