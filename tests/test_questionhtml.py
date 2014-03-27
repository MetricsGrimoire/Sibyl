# Copyright (C) 2014 Bitergia
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:
#         Daniel Izquierdo Cortazar <dizquierdo@bitergia.com>
#

# This file aims at testing the HTML parser of each page in askbot backend

import sys
import unittest
from BeautifulSoup import BeautifulSoup

from pysibyl.askbot import QuestionHTML

FILE_PATH = "tests/data/ask.openstack.org.25627.html"
FILE_PATH_0_ANSWERS = "tests/data/ask.openstack.org.25960.html"
FILE_PATH_6_ANSWERS = "tests/data/ask.openstack.org.21353.html"

class TestQuestionHTML(unittest.TestCase):
    """Tests for QuestionHTML class
    """

    def _read_file(self, file_path):
        # function to read test cases
        fd = open(file_path, "r")
        return fd.read()
    
    

    def test_parser(self):
        # function to parse url locally stored
        # and test general information

        BODY_TEST = "how can i use Openstack's authentication api with Python plzz..im gettin always the same error 401 (im tryin to acces Keystone with Python program and i need to post some credentials)"
        TAGS_TEST = [u'python', u'keystone#openstack', u'error401', u'Ask', u' OpenStack', u'forum', u'community', u'cloud', u'iaas'] 
        ANSWER_BODYTEST = """answered2014-03-20 10:50:03 -0500Bill@Metacloud256&#9679;4&#9679;5http://www.metacloud.com/updated2014-03-20 11:19:31 -0500I done this with Python locally, here is a snip of code using v2.0 auth withhttp://example.com:5000/v2.0from keystoneclient.v2_0 import clientkeystone = client.Client(username="admin", password="Password_here", tenant_name="Admin", auth_url="http://api-example.client.acme.net:5000/v2.0")this will get you in, then you need to do what ever it is you wanting to do."""

        # Fake URL
        URL = "http://www.example.com/"
        questionHTML = QuestionHTML(URL)

        # Overwritting variable bsoup that contains HTML
        fd = open(FILE_PATH, "r")
        html = fd.read()
        html = self._read_file(FILE_PATH)
        questionHTML.bsoup = BeautifulSoup(html)
        
        body =  questionHTML.getBody() 
        tags = questionHTML.getTags()
        answers = questionHTML.getAnswers(1) #fake question id

        self.assertEqual(BODY_TEST, body)
        self.assertEqual(TAGS_TEST, tags)
        self.assertEqual(len(answers), 1)

        answer = answers[0]

        self.assertEqual(answer.identifier, 25632)
        self.assertEqual(answer.body, ANSWER_BODYTEST)
        self.assertEqual(answer.user_identifier, u'2106') 
        self.assertEqual(answer.submitted_on, '2014-03-20 10:50:03 -0500')
        self.assertEqual(answer.votes, 0)

    def test_answers(self):
        # function to test number of answers in 
        # several data files

        # Fake URL
        URL = "http://www.example.com/"
        questionHTML = QuestionHTML(URL)
        # Overwritting variable bsoup that contains HTML
        html = self._read_file(FILE_PATH_0_ANSWERS)
        questionHTML.bsoup = BeautifulSoup(html)
        answers = questionHTML.getAnswers(1) #fake question id
        
        self.assertEqual(0, len(answers))

        # Fake URL
        URL = "http://www.example.com/"
        questionHTML = QuestionHTML(URL)
        # Overwritting variable bsoup that contains HTML
        html = self._read_file(FILE_PATH_6_ANSWERS)
        questionHTML.bsoup = BeautifulSoup(html)
        answers = questionHTML.getAnswers(1) #fake question id

        self.assertEqual(6, len(answers))

    def test_tags(self):
        # function that tests number of tags and tags per file
        TAGS_FILE_PATH = [u'rdo', u'Ask', u' OpenStack', u'forum', u'community', u'cloud', u'iaas']
        TAGS_FILE_PATH_6_ANSWERS = [u'cinder', u'migrated', u'Ask', u' OpenStack', u'forum', u'community', u'cloud', u'iaas']
        TAGS_FILE_PATH_0_ANSWERS = [u'python', u'keystone#openstack', u'error401', u'Ask', u' OpenStack', u'forum', u'community', u'cloud', u'iaas']
        
        # Fake URL
        URL = "http://www.example.com/"
        questionHTML = QuestionHTML(URL)
        # Overwritting variable bsoup that contains HTML
        html = self._read_file(FILE_PATH_0_ANSWERS)
        questionHTML.bsoup = BeautifulSoup(html)
        tags = questionHTML.getTags() #fake question id
        self.assertEqual(7, len(tags))
        self.assertEqual(TAGS_FILE_PATH, tags)

        # Fake URL
        URL = "http://www.example.com/"
        questionHTML = QuestionHTML(URL)
        # Overwritting variable bsoup that contains HTML
        html = self._read_file(FILE_PATH_6_ANSWERS)
        questionHTML.bsoup = BeautifulSoup(html)
        tags = questionHTML.getTags() #fake question id
        self.assertEqual(8, len(tags))
        self.assertEqual(TAGS_FILE_PATH_6_ANSWERS, tags)

        # Fake URL
        URL = "http://www.example.com/"
        questionHTML = QuestionHTML(URL)
        # Overwritting variable bsoup that contains HTML
        html = self._read_file(FILE_PATH)
        questionHTML.bsoup = BeautifulSoup(html)
        tags = questionHTML.getTags() #fake question id
        self.assertEqual(9, len(tags))
        self.assertEqual(TAGS_FILE_PATH_0_ANSWERS, tags)




if __name__ == "__main__":
    unittest.main()

