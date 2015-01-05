#!/usr/bin/python
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
#   Daniel Izquierdo Cortazar <dizquierdo@bitergia.com>
#   Alvaro del Castillo <acs@bitergia.com>
#

import logging

from optparse import OptionParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pysibyl.db import Base
from pysibyl.askbot import Askbot
from pysibyl.stackoverflow import Stack

def read_options():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 0.1")
    parser.add_option("-t", "--type",
                      action="store",
                      dest="type",
                      help="Type: askbot (ab), stackoverflow")
    parser.add_option("-l", "--url",
                      action="store",
                      dest="url",
                      help="URL to analyze")
    parser.add_option("-d", "--database",
                      action="store",
                      dest="dbname",
                      help="Database where information is stored")
    parser.add_option("-u", "--db-user",
                      action="store",
                      dest="dbuser",
                      default="root",
                      help="Database user")
    parser.add_option("-p", "--db-password",
                      action="store",
                      dest="dbpassword",
                      default="",
                      help="Database password")
    parser.add_option("-g", "--debug",
                      action="store_true",
                      dest="debug",
                      default=False,
                      help="Debug mode")
    parser.add_option("-k", "--key",
                      action="store",
                      dest="api_key",
                      help="API key")
    parser.add_option("--tags",
                      action="store",
                      dest="tags",
                      help="Tags to be gathered")

    (opts, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("Wrong number of arguments")

    if not opts.url or not opts.dbuser or not opts.dbuser or not opts.type:
        parser.error("url, dbuser, database and type are needed params")

    if (opts.type == "stackoverflow" and not (opts.api_key and opts.tags)):
        parser.error("key and tags are need for stackoverflow.")

    return opts

def askbot_parser(session, url):
    # Initial parsing of general info, users and questions

    askbot = Askbot(url)
    all_users = []

    for questionset in askbot.questions():
        users_id = []
        for dbquestion in questionset:
            # TODO: at some point the questions() iterator should
            # provide each "question" and not a set of them
            print "Analyzing: " + dbquestion.url

            updated, found = askbot.is_question_updated(dbquestion, session)
            if found and updated:
                # no changes needed
                print "    * NOT updating information for this question"
                continue

            if found and not updated:
                # So far using the simpliest approach: remove all info related to
                # this question and re-insert values: drop question, tags, 
                # answers and comments for question and answers.
                # This is done in this way to avoid several 'if' clauses to 
                # control if question was found/not found or updated/not updated
                print "Restarting dataset for this question"
                askbot.remove_question(dbquestion, session)

            dbquestion = askbot.get_question(dbquestion)
            users_id.append(dbquestion.author_identifier)
            session.add(dbquestion)
            session.commit()

            #Comments
            comments = askbot.question_comments(dbquestion)
            for comment in comments:
                session.add(comment)
                session.commit()

            #Answers
            answers = askbot.answers(dbquestion)
            for answer in answers:
                if answer.user_identifier is not None:
                    users_id.append(answer.user_identifier)
                session.add(answer)
                session.commit()
                # comments per answer
                comments = askbot.answer_comments(answer)
                for comment in comments:
                    session.add(comment)
                    session.commit()

            #Tags
            tags, questiontags = askbot.tags(dbquestion)
            for tag in tags:
                session.add(tag)
                session.commit()
            for questiontag in questiontags:
                session.add(questiontag)
                session.commit()

            #Users
            for user_id in users_id:
                if user_id not in all_users:
                    #User not previously inserted
                    user = askbot.get_user(user_id)
                    session.add(user)
                    session.commit()
                    all_users.append(user_id)

def stack_parser(session):
    # Initial parsing of general info, users and questions
    url = opts.url
    tags = opts.tags.split(",")
    stack = Stack(url, opts.api_key, opts.tags)
    all_users = []

    logging.info("Stack parsing from: " + opts.url)

    if len(tags) == 1:
        # If just one tag, we try to find others
        tags = stack.get_search_tags()

    for tag in tags:
        questions = stack.questions(tag)
        users_id = []

        logging.info("Analyzing queries received " + str(len(questions)))
        done = 0

        for dbquestion in questions:
            # TODO: at some point the questions() iterator should
            # provide each "question" and not a set of them
            logging.debug ("Analyzing: " + dbquestion.url)

            if done % 100 == 0: logging.info (str(done)+"/"+str(len(questions)))
            done += 1

            updated, found = stack.is_question_updated(dbquestion, session)
            if found and updated:
                # no changes needed
                logging.debug ("    * NOT updating information for this question")
                continue

            if found and not updated:
                # So far using the simpliest approach: remove all info related to
                # this question and re-insert values: drop question, tags, 
                # answers and comments for question and answers.
                # This is done in this way to avoid several 'if' clauses to 
                # control if question was found/not found or updated/not updated
                logging.debug ("Restarting dataset for this question")
                stack.remove_question(dbquestion, session)

            users_id.append(dbquestion.author_identifier)
            session.add(dbquestion)
            session.commit()

            # Tags
            questiontags = stack.get_dbquestiontags(dbquestion.id, dbquestion.tags, session)
            for questiontag in questiontags:
                session.add(questiontag)
                session.commit()

            continue

            # Comments
            comments = stack.get_comments(dbquestion,"question")
            for comment in comments:
                session.add(comment)
                session.commit()

            # Answers
            answers = stack.answers(dbquestion)
            for answer in answers:
                users_id.append(answer.user_identifier)
                session.add(answer)
                session.commit()
                # comments per answer
                comments = stack.get_comments(answer, "answer")
                for comment in comments:
                    session.add(comment)
                    session.commit()

            #Users
            for user_id in users_id:
                if user_id not in all_users:
                    #User not previously inserted
                    user = stack.get_user(user_id)
                    if user is None:
                        logging.error("None user found")
                        continue
                    session.add(user)
                    session.commit()
                    all_users.append(user_id)

        logging.info (str(done)+"/"+str(len(questions)))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')

    opts = read_options()

    options = """mysql://%s:%s@localhost/%s?charset=utf8""" % (opts.dbuser, opts.dbpassword, opts.dbname)
    engine = create_engine(options, encoding = 'utf-8')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Previously create database with 
    # CREATE DATABASE <database> CHARACTER SET utf8 COLLATE utf8_unicode_ci;
    Base.metadata.create_all(engine)

    session.commit()

    if opts.type == "ab":
        # askbot backend
        askbot_parser(session, opts.url)
    elif opts.type == "stackoverflow":
        # askbot backend
        stack_parser(session)
    else:
        logging.error("Type not supported: " + opts.type)
