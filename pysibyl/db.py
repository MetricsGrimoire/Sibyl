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
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, Text


Base = declarative_base()
# Create MySQL database flavour as:
# CREATE DATABASE <database> CHARACTER SET utf8 COLLATE utf8_unicode_ci;


class People(Base):
    """Contains information about people participating in questions, comments or answers
    """

    __tablename__ = 'people'

    id = Column(Integer, primary_key = True) # Unique id
    username =  Column(String(50))
    joined_at = Column(DateTime, nullable = False)
    last_seen_at = Column(DateTime, nullable = False)
    reputation = Column(Integer)
    avatar = Column(String(256))
    user_identifier = Column(Integer) # Unique user id in the analyzed repository


class Questions(Base):
    """Contains information about all of the questions found in a QA tool
    """

    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True) # Unique id
    answer_count = Column(Integer)
    question_identifier = Column(Integer) # Unique question id used in the analyzed repo
    view_count = Column(Integer)
    last_activity_at = Column(DateTime, nullable=False)
    last_activity_by = Column(Integer) 
    title = Column(String(256))
    body = Column(Text())
    url = Column(String(256))
    score = Column(Integer)
    added_at = Column(DateTime, nullable=False)
    author = Column(Integer)


class QuestionsTags(Base):
    """Contains links for the tags assigned to each question
    """

    __tablename__ = 'questionstags'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer)
    tag_id = Column(Integer)


class Tags(Base):
    """List of tags
    """

    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag = Column(String(50))


class Answers(Base):
    """List of answers found for each question
    """

    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    identifier = Column(Integer)
    body = Column(Text())
    user_id = Column(Integer)
    question_id = Column(Integer)
    submitted_on = Column(DateTime, nullable=False)
    votes = Column(Integer)

    
class Comments(Base):
    """Comments done either to Answers or Questions
    """

    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer)
    answer_id = Column(Integer)
    body = Column(Text())
    user_id = Column(Integer)
    submitted_on = Column(DateTime, nullable=False)


