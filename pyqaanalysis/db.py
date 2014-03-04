# Database module
#
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
#    Daniel Izquierdo Cortazar <dizquierdo@bitergia.com>   
#

from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class People(Base):
    # People table: contains information about people participating
    #               in questions, comments or answers
    __tablename__ = 'people'
    id = Column(Integer, primary_key = True) # Unique id
    nickname =  Column(String(50))
    joined_at = Column(DateTime, nullable = False)
    reputation = Column(Integer)
    avatar = Column(String(256))
    user_identifier = Column(Integer) # Unique user id in the analyzed repository

class Questions(Base):
    # Questions table: contains information about all of the questions
    #                  found in a QA tool
    __tablename__ = 'questions'
    id = Column(Integer, primary_key = True) # Unique id
    answer_count = Column(Integer)
    question_identifier = Column(Integer) # Unique question id used in the analyzed repo
    view_count = Column(Integer)
    last_updated = Column(DateTime, nullable = False)
    title = Column(String(256))
    body = Column(Text())
    URL = Column(String(256)
    score = Column(Integer)
    submitted_on = Column(DateTime, nullable = False)

class QuestionsTags(Base):
    # QuestionsTags table: contains links for the tags assigned to each question
    __tablename__ = 'questionstags'
    id = Column(Integer, primary_key = True)
    question_id = Column(Integer)
    tag_id = Column(Integer)

class Tags(Base):
    # Tags table: list of tags
    __tablename__ = 'tags'
    id = Column(Integer, primary_key = True)
    tag = Column(Strin(50))

class Answers(Base):
    # Answers table: list of answers found for each question
    __tablename__ = 'answers'
    id = Column(Integer, primary_key = True)
    body = Column(Text())
    user_id = Column(Integer)
    question_id = Column(Integer)
    submitted_on = Column(DateTime, nullable = False)
    
class Comments(Base):
    # Comments table: comments done either to Answers or Questions
    __tablename__ = 'comments'
    id = Column(Integer, primary_key = True)
    question_id = Column(Integer)
    answer_id = Column(Integer)
    body = Column(Text())
    user_id = Column(Integer)
    submitted_on = Column(DateTime, nullable = False)


