# Copyright (C) 2012-2013 Bitergia
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
#

from optparse import OptionParser
import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker

import requests

from BeautifulSoup import BeautifulSoup 

from pysibyl.db import Base, People, Questions, Tags, QuestionsTags, Answers
from pysibyl.utils import JSONParser
from pysibyl.askbot import Askbot


def read_options():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 0.1")
    parser.add_option("-t", "--type",
                      action="store",
                      dest="type",
                      help="Type: askbot (ab)")
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
    (opts, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("Wrong number of arguments")

    return opts

def askbot_parser(session, url):
    # Initial parsing of general info, users and questions

    askbot = Askbot(url)
    all_users = []

    for questionset in askbot.questions():
        users_id = []
        for question_id in questionset:
            # TODO: at some point the questions() iterator should
            # provide each "question" and not a set of them
            question = askbot.get_question(question_id)
            users_id.append(question.author)
            session.add(question)
            session.commit()
    
            #Answers
            answers = askbot.answers(question)
            for answer in answers:
                users_id.append(answer.user_identifier)
                session.add(answer)
                session.commit()

            #Tags
            tags, questiontags = askbot.tags(question)
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
                    all_users.append(user)
                

if __name__ == '__main__':
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

        
