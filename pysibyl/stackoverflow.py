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
# Parser for Stackoverflow QA tool

import datetime
import logging
import re
import requests

from pysibyl.db import People, Questions, Tags, QuestionsTags, Answers, Comments
from pysibyl.utils import JSONParser

class StackSampleData(object):
    """Sample data from StackExchange API to debug without doing real queries"""
    @staticmethod
    def init():
        # results for questions with openshift-enterprise
        StackSampleData.questions_1 = '{"items":[{"tags":["ubuntu","openshift","openshift-enterprise"],"owner":{"reputation":983,"user_id":2859018,"user_type":"registered","accept_rate":83,"profile_image":"http://i.stack.imgur.com/CXfZu.jpg?s=128&g=1","display_name":"sriraman","link":"http://stackoverflow.com/users/2859018/sriraman"},"is_answered":true,"view_count":25,"accepted_answer_id":27407422,"answer_count":1,"score":0,"last_activity_date":1418233248,"creation_date":1418231440,"question_id":27406879,"link":"http://stackoverflow.com/questions/27406879/uploaded-files-getting-deleted-while-redeploying-in-openshift-server","title":"Uploaded files getting deleted while redeploying in Openshift server"},{"tags":["tomcat","phpmyadmin","openshift","openshift-origin","openshift-enterprise"],"owner":{"reputation":646,"user_id":1354334,"user_type":"registered","accept_rate":92,"profile_image":"http://i.stack.imgur.com/GUqsL.jpg?s=128&g=1","display_name":"Saif","link":"http://stackoverflow.com/users/1354334/saif"},"is_answered":true,"view_count":65,"accepted_answer_id":27399147,"answer_count":1,"score":0,"last_activity_date":1418208729,"creation_date":1412945601,"last_edit_date":1412963653,"question_id":26299939,"link":"http://stackoverflow.com/questions/26299939/err-ssl-protocol-error-when-accessing-phpmyadmin-on-my-openshift-domain","title":"ERR_SSL_PROTOCOL_ERROR when accessing phpmyadmin on my openshift domain"},{"tags":["git","ssh","openshift","ssh-keys","openshift-enterprise"],"owner":{"reputation":153,"user_id":3490411,"user_type":"registered","accept_rate":42,"profile_image":"https://www.gravatar.com/avatar/0334225d0a38d5a9949beb0beed9901a?s=128&d=identicon&r=PG&f=1","display_name":"nmkkannan","link":"http://stackoverflow.com/users/3490411/nmkkannan"},"is_answered":true,"view_count":48,"accepted_answer_id":27143884,"answer_count":2,"score":0,"last_activity_date":1417066356,"creation_date":1416987977,"question_id":27143724,"link":"http://stackoverflow.com/questions/27143724/rhc-ssh-no-system-ssh-available-error","title":"rhc ssh [No system SSH available] error"},{"tags":["openshift","openshift-origin","openshift-enterprise"],"owner":{"reputation":294,"user_id":2585791,"user_type":"registered","accept_rate":49,"profile_image":"https://www.gravatar.com/avatar/ab50cfe8364f261480605c803c15c60e?s=128&d=identicon&r=PG&f=1","display_name":"Charnjeet","link":"http://stackoverflow.com/users/2585791/charnjeet"},"is_answered":false,"view_count":42,"answer_count":1,"score":0,"last_activity_date":1415790776,"creation_date":1415630755,"question_id":26846345,"link":"http://stackoverflow.com/questions/26846345/unable-to-deploy-war-file-on-openshipt-using-git","title":"Unable to Deploy War file on OpenShipt using git"},{"tags":["tomcat","redirect","openshift","ofbiz","openshift-enterprise"],"owner":{"reputation":15,"user_id":3921566,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/f8cbc6a821eb7a856097b616f04fd6b4?s=128&d=identicon&r=PG&f=1","display_name":"Vinay Saini","link":"http://stackoverflow.com/users/3921566/vinay-saini"},"is_answered":false,"view_count":22,"answer_count":0,"score":0,"last_activity_date":1415093611,"creation_date":1415093611,"question_id":26731739,"link":"http://stackoverflow.com/questions/26731739/redirect-url-in-diy-openshift","title":"Redirect URL in DIY openshift"},{"tags":["openshift-origin","openshift-enterprise"],"owner":{"reputation":13,"user_id":2934258,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/7ba12dafb49d459fc29410c1de3eff81?s=128&d=identicon&r=PG","display_name":"Al Sargent","link":"http://stackoverflow.com/users/2934258/al-sargent"},"is_answered":false,"view_count":34,"answer_count":0,"score":0,"last_activity_date":1410808736,"creation_date":1410797826,"last_edit_date":1410808736,"question_id":25852447,"link":"http://stackoverflow.com/questions/25852447/what-is-the-difference-between-openshift-origin-and-openshift-enterprise","title":"What is the difference between OpenShift Origin and OpenShift Enterprise?"},{"tags":["mongodb","openshift-enterprise"],"owner":{"reputation":1,"user_id":4026756,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/b3b2dfe64b3200d82162dd8a1687bf2d?s=128&d=identicon&r=PG&f=1","display_name":"jaygerbomb","link":"http://stackoverflow.com/users/4026756/jaygerbomb"},"is_answered":true,"view_count":18,"answer_count":1,"score":0,"last_activity_date":1410358109,"creation_date":1410351105,"last_edit_date":1410358109,"question_id":25765161,"link":"http://stackoverflow.com/questions/25765161/corrupt-openshift-broker-database-and-running-apps","title":"Corrupt openshift broker database and running apps"},{"tags":["openshift-enterprise"],"owner":{"reputation":1,"user_id":3816248,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/751179b1c70e7a77ae71a0a2b614680f?s=128&d=identicon&r=PG&f=1","display_name":"john","link":"http://stackoverflow.com/users/3816248/john"},"is_answered":false,"view_count":19,"answer_count":0,"score":0,"last_activity_date":1409930848,"creation_date":1404821040,"last_edit_date":1409930848,"question_id":24631393,"link":"http://stackoverflow.com/questions/24631393/expected-behaviour-of-gears-when-node-goes-offline","title":"Expected behaviour of gears when node goes offline"}],"has_more":false,"quota_max":10000,"quota_remaining":9983}'
        # results for 5 questions with openshift
        StackSampleData.questions = '{"items":[{"tags":["java","websocket","openshift","wildfly-8","tyrus"],"owner":{"reputation":1,"user_id":1247758,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/f94153a2df2b2c6c59ea7154a1e027cb?s=128&d=identicon&r=PG","display_name":"H_DANILO","link":"http://stackoverflow.com/users/1247758/h-danilo"},"is_answered":false,"view_count":8,"answer_count":0,"score":0,"last_activity_date":1420258632,"creation_date":1420258632,"question_id":27751666,"link":"http://stackoverflow.com/questions/27751666/websocket-with-tyrus-in-openshift","title":"Websocket with Tyrus in Openshift"},{"tags":["node.js","meteor","openshift"],"owner":{"reputation":18,"user_id":4138707,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/34b5da802942dc3d899028636434665e?s=128&d=identicon&r=PG&f=1","display_name":"ViktorW","link":"http://stackoverflow.com/users/4138707/viktorw"},"is_answered":true,"view_count":193,"accepted_answer_id":26446266,"answer_count":2,"score":3,"last_activity_date":1420248047,"creation_date":1413227541,"question_id":26347214,"link":"http://stackoverflow.com/questions/26347214/deploy-meteor-8-3-and-higher-on-openshift","title":"Deploy meteor 8.3 and higher on openshift"},{"tags":["openshift","bower"],"owner":{"reputation":91,"user_id":3915717,"user_type":"registered","accept_rate":62,"profile_image":"https://www.gravatar.com/avatar/a4aeb9a743d09f53ac9b8aed32d7ae93?s=128&d=identicon&r=PG&f=1","display_name":"SuperUberDuper","link":"http://stackoverflow.com/users/3915717/superuberduper"},"is_answered":false,"view_count":19,"answer_count":1,"score":0,"last_activity_date":1420232350,"creation_date":1419614882,"last_edit_date":1419857639,"question_id":27660010,"link":"http://stackoverflow.com/questions/27660010/trying-to-run-bower-install-on-an-openshift-app","title":"Trying to run bower install on an openshift app"},{"tags":["java","maven","openshift"],"owner":{"reputation":23,"user_id":3813853,"user_type":"registered","accept_rate":83,"profile_image":"http://i.stack.imgur.com/8xm8g.png?s=128&g=1","display_name":"jenova","link":"http://stackoverflow.com/users/3813853/jenova"},"is_answered":false,"view_count":25,"answer_count":0,"score":0,"last_activity_date":1420229659,"creation_date":1420216026,"last_edit_date":1420229659,"question_id":27745223,"link":"http://stackoverflow.com/questions/27745223/openshift-war-successfully-deployed-but-i-still-see-the-default-welcome-page","title":"Openshift war successfully deployed but I still see the default welcome page"},{"tags":["openshift","jena","fuseki"],"owner":{"reputation":568,"user_id":1789384,"user_type":"registered","accept_rate":77,"profile_image":"https://www.gravatar.com/avatar/ffa6f71039348b4b0724f9403791b55b?s=128&d=identicon&r=PG","display_name":"Drux","link":"http://stackoverflow.com/users/1789384/drux"},"is_answered":false,"view_count":19,"answer_count":1,"score":0,"last_activity_date":1420228289,"creation_date":1420184997,"last_edit_date":1420195057,"question_id":27739072,"link":"http://stackoverflow.com/questions/27739072/fuseki-on-openshift-can-update-but-not-select","title":"Fuseki on OpenShift: Can UPDATE but not SELECT"}],"has_more":true,"quota_max":10000,"quota_remaining":9950}'
        # tags including openshift
        StackSampleData.tags = '{"items":[{"has_synonyms":false,"is_moderator_only":false,"is_required":false,"count":1985,"name":"openshift"},{"has_synonyms":false,"is_moderator_only":false,"is_required":false,"count":71,"name":"openshift-origin"},{"has_synonyms":false,"is_moderator_only":false,"is_required":false,"count":20,"name":"openshift-client-tools"},{"has_synonyms":false,"is_moderator_only":false,"is_required":false,"count":8,"name":"openshift-enterprise"},{"has_synonyms":false,"is_moderator_only":false,"is_required":false,"count":1,"name":"openshift-web-console"}],"has_more":false,"quota_max":10000,"quota_remaining":9992}'
        # Question comments sample
        StackSampleData.comments = '{"items":[{"owner":{"reputation":20251,"user_id":313063,"user_type":"registered","accept_rate":85,"profile_image":"https://www.gravatar.com/avatar/64afa42ebc0a920509f959e97307d16f?s=128&d=identicon&r=PG","display_name":"Andr&#233; Caron","link":"http://stackoverflow.com/users/313063/andr%c3%a9-caron"},"reply_to_user":{"reputation":101,"user_id":1073106,"user_type":"registered","profile_image":"http://i.stack.imgur.com/sZlKX.jpg?s=128&g=1","display_name":"Martin Argerami","link":"http://stackoverflow.com/users/1073106/martin-argerami"},"edited":false,"score":0,"creation_date":1369237962,"post_id":13,"comment_id":24030385},{"owner":{"reputation":11286,"user_id":219883,"user_type":"registered","accept_rate":91,"profile_image":"https://www.gravatar.com/avatar/c35b5b0f9e7cce48864f4f1545ead995?s=128&d=identicon&r=PG","display_name":"Taryn East","link":"http://stackoverflow.com/users/219883/taryn-east"},"edited":false,"score":0,"creation_date":1367713606,"post_id":13,"comment_id":23475402},{"owner":{"reputation":1708,"user_id":14978,"user_type":"registered","accept_rate":14,"profile_image":"https://www.gravatar.com/avatar/16cb3584428bed67b10a33f628d5b009?s=128&d=identicon&r=PG","display_name":"catphive","link":"http://stackoverflow.com/users/14978/catphive"},"edited":false,"score":17,"creation_date":1302295789,"post_id":13,"comment_id":6376998},{"owner":{"reputation":1781,"user_id":254896,"user_type":"registered","accept_rate":55,"profile_image":"https://www.gravatar.com/avatar/516483be71b517eae14dc24c2bb39bda?s=128&d=identicon&r=PG","display_name":"agnoster","link":"http://stackoverflow.com/users/254896/agnoster"},"edited":false,"score":3,"creation_date":1289465298,"post_id":13,"comment_id":21790488},{"owner":{"reputation":6430,"user_id":26682,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/04ba362109d3862660d4b1b0b3f2d923?s=128&d=identicon&r=PG","display_name":"Rob Williams","link":"http://stackoverflow.com/users/26682/rob-williams"},"edited":false,"score":2,"creation_date":1228179087,"post_id":13,"comment_id":21790487}],"has_more":false,"quota_max":10000,"quota_remaining":9946}'

class Stack(object):
    """Stack main class
    """

    def __init__(self, url, api_key, tags):
        self.url = url
        self.questionHTML = None #Current question working on
        self.alltags = []
        self.allusers =  []
        self.api_key = api_key
        self.tags = tags
        self.debug = True
        StackSampleData.init()

    def _get_url(self):
        return self.url + "/2.2/tags?key="+self.api_key+"&"

    def questions(self, tag):
        questions = []
        url = self.url + '/2.2/questions?'
        url += 'order=desc&sort=activity&site=stackoverflow&key='+self.api_key+'&'
        url += 'tagged='+ tag
        logging.info("Getting questions for " + tag)
        if not self.debug:
            stream = requests.get(url, verify=False)
            data = stream.text
            print(data)
        else:
            data = StackSampleData.questions

        parser = JSONParser(unicode(data))
        parser.parse()
        # [u'has_more', u'items', u'quota_max', u'quota_remaining']
        data = parser.data['items']

        for question in data:
            # Each of the question is initialized here
            # [u'is_answered', u'view_count', u'tags', u'last_activity_date', u'answer_count', u'creation_date', 
            # u'score', u'link', u'accepted_answer_id', u'owner', u'title', u'question_id']
            dbquestion = Questions()
            dbquestion.author_identifier = question['owner']
            dbquestion.answer_count = question['answer_count']
            dbquestion.question_identifier = question['question_id']
            dbquestion.view_count = question['view_count']
            if question['last_activity_date'] is not None:
                dbquestion.last_activity_at = datetime.datetime.fromtimestamp(int(question['last_activity_date'])).strftime('%Y-%m-%d %H:%M:%S')
            else:
                dbquestion.last_activity_at = datetime.datetime.fromtimestamp(int(question['creation_date'])).strftime('%Y-%m-%d %H:%M:%S')
            dbquestion.title = question['title']
            dbquestion.url = question['link']
            dbquestion.added_at = datetime.datetime.fromtimestamp(int(question['creation_date'])).strftime('%Y-%m-%d %H:%M:%S')
            dbquestion.score = question['score']
            # Missing fields in Stack
            dbquestion.last_activity_by = None
            dbquestion.body = None # TODO: we need to get it
            # Additional fields in Stack: is_answered, accepted_answer_id

            questions.append(dbquestion)

        return questions


    def get_search_tags(self):
        found_tags = []

        logging.info("Getting all task based on: " + self.tags)
        url = self._get_url()
        url += "order=desc&sort=popular&site=stackoverflow"
        url += "&inname=" + str(self.tags)
        if not self.debug:
            stream = requests.get(url, verify=False)
            data = stream.text
        else:
            data = StackSampleData.tags

        parser = JSONParser(unicode(data))
        parser.parse()
        tags_data = parser.data['items']
        for tag in tags_data:
            found_tags.append(tag['name'])

        return found_tags

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


    def get_comments(self, dbpost, kind = 'question'):
        # coments associated to a post (question or answer) that question
        url = self.url
        dbcomments = []
        if kind == 'question': url = self.url + '/2.2/questions/'
        if kind == 'question': url = self.url + '/2.2/answers/'
        url += str(dbpost.id) +'/comments?'
        url += 'order=desc&sort=creation&site=stackoverflow&key='+self.api_key+'&'
        print(url)
        logging.info("Getting comments for " + dbpost.title)
        if not self.debug:
            stream = requests.get(url, verify=False)
            data = stream.text
            print (data)
        else:
            data = StackSampleData.comments

        parser = JSONParser(unicode(data))
        parser.parse()
        # [u'has_more', u'items', u'quota_max', u'quota_remaining']
        data = parser.data['items']

        for comment in data:
            dbcomment = Comments()

            # question or answer identifier
            if kind == "question":
                dbcomment.question_identifier = dbpost.id
            if kind == "answer":
                dbcomment.answer_identifier = dbpost.id
            if 'body' in comment.keys(): dbcomment.body = comment.body

            dbcomment.user_identifier = comment.owner
            cdate = datetime.datetime.fromtimestamp(int(comment['creation_date']))
            dbcomment.submitted_on = cdate.strftime('%Y-%m-%d %H:%M:%S')
            dbcomments.append(dbcomment)

        return dbcomments

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
