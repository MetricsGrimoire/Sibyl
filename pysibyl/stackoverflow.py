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
# Parser for Stackoverflow tool using https://api.stackexchange.com

import datetime
import json
import logging
import requests
import time

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
        # Question answer sample
        StackSampleData.answers = '{"items":[{"owner":{"reputation":128,"user_id":2241405,"user_type":"registered","accept_rate":67,"profile_image":"https://www.gravatar.com/avatar/c1116dfd17a4e1c51736b9e4a8a54d32?s=128&d=identicon&r=PG","display_name":"AkoSi Asiong","link":"http://stackoverflow.com/users/2241405/akosi-asiong"},"is_accepted":false,"community_owned_date":1365692915,"score":11,"last_activity_date":1419095927,"last_edit_date":1419095927,"creation_date":1365692915,"answer_id":15952367,"question_id":4},{"owner":{"reputation":8536,"user_id":39,"user_type":"registered","accept_rate":76,"profile_image":"https://www.gravatar.com/avatar/ea7063d6a51a923ca945008d137aaaa0?s=128&d=identicon&r=PG","display_name":"huseyint","link":"http://stackoverflow.com/users/39/huseyint"},"is_accepted":false,"score":61,"last_activity_date":1405089748,"last_edit_date":1405089748,"creation_date":1217600608,"answer_id":86,"question_id":4},{"owner":{"reputation":139,"user_id":1391700,"user_type":"registered","profile_image":"https://www.gravatar.com/avatar/fa3e75ad5d1b10a30f05a67a84c8a85c?s=128&d=identicon&r=PG","display_name":"Darryl","link":"http://stackoverflow.com/users/1391700/darryl"},"is_accepted":false,"score":11,"last_activity_date":1350215708,"last_edit_date":1350215708,"creation_date":1336875025,"answer_id":10568821,"question_id":4},{"owner":{"reputation":5343,"user_id":55,"user_type":"registered","accept_rate":90,"profile_image":"https://www.gravatar.com/avatar/fcc79759f6398caee5df36cde61b36b7?s=128&d=identicon&r=PG","display_name":"Ryan Fox","link":"http://stackoverflow.com/users/55/ryan-fox"},"is_accepted":false,"score":27,"last_activity_date":1350215680,"last_edit_date":1350215680,"creation_date":1217598786,"answer_id":78,"question_id":4},{"owner":{"reputation":16611,"user_id":356,"user_type":"registered","accept_rate":100,"profile_image":"https://www.gravatar.com/avatar/d7903d8d8a0ef0b446d12906bc32dae8?s=128&d=identicon&r=PG","display_name":"Dinah","link":"http://stackoverflow.com/users/356/dinah"},"is_accepted":false,"score":21,"last_activity_date":1350215663,"last_edit_date":1350215663,"creation_date":1227191802,"answer_id":305467,"question_id":4}],"has_more":true,"quota_max":10000,"quota_remaining":9971}'
        # User
        StackSampleData.users = '{"items":[{"badge_counts":{"bronze":121,"silver":93,"gold":20},"account_id":285,"is_employee":false,"last_modified_date":1406421468,"last_access_date":1420310000,"reputation_change_year":5,"reputation_change_quarter":5,"reputation_change_month":5,"reputation_change_week":0,"reputation_change_day":0,"reputation":16611,"creation_date":1217898789,"user_type":"registered","user_id":356,"age":35,"accept_rate":100,"location":"North Carolina","website_url":"","link":"http://stackoverflow.com/users/356/dinah","display_name":"Dinah","profile_image":"https://www.gravatar.com/avatar/d7903d8d8a0ef0b446d12906bc32dae8?s=128&d=identicon&r=PG"}],"has_more":false,"quota_max":10000,"quota_remaining":9961}'
        # Users ids
        StackSampleData.users_ids = '1122983;1237811;1376515;856634;725306;4209131;2034990;2617491;2547973;1339560;3248801;2377988;2052543;3854255;1496037;4124834;729403;1906518;3849477;2700550;4201189;2517338;2159867;379235;2085626;4204340;2072156;818075;1549354;3647002;1290530;3773466;2902165;3576706;3423953;4227698;801354;818716;4230374;2980517;1348379;3827568;1136372;4183485;1106178;4234491;3814640;3666184;2669143;1578941;1809645;2585791;4245183;638052;2207529;445190;4233219;1953145;3480706;4056263;1921070;4132925;4252762;1189959;2393622;3681243;2317607;2187846;1349189;3538533;223934;120606;1974184;2312688;786326;3966820;2329208;3101102;3170123;2211642;3593497;3073861;4270940;348081;2796352;1184247;3405979;4211123;1382814;2580412;1945334;3442820;4284380;3849972;3567546;368532;3655193;1361087;1658441;4269564'

class Stack(object):
    """Stack main class"""

    def __init__(self, url, api_key, tags, session):
        self.url = url
        self.questionHTML = None #Current question working on
        self.alltags = []
        self.allusers =  []
        self.api_key = api_key
        self.tags = tags
        self.debug = False
        self.dbtags = []
        self.session = session
        self.pagesize = 100 # max for stacjoverflow
        self.api_limit = 10000 # max default
        self.api_queries = 0
        self.user_ids_questions = []
        self.user_ids_answers = []
        self.user_ids_comments = []
        self.total_users = 0
        self.total_questions = 0
        self.total_answers = 0
        self.total_comments = 0
        StackSampleData.init()

    def _get_api_data(self, url):
        logging.info(url)
        stream = requests.get(url, verify=False)
        self.api_queries += 1
        data = stream.text
        try:
            if 'quota_remaining' in stream.json():
                self.api_limit = stream.json()['quota_remaining']
                if self.api_limit % 100 == 0:
                    logging.info("Quota remaining " + str(self.api_limit))
                if self.api_limit < 10:
                    logging.info("API consumed. Can't continue")
                    raise Exception
            if 'backoff' in stream.json():
                # We must wait backoff seconds before continuing
                backoff = stream.json()['backoff']
                logging.info("Waiting " + str(backoff) + " seconds as backoff request from API.")
                time.sleep(backoff)
        except:
            logging.error("No JSON answer from Stack API")
            print data
            raise Exception
        logging.debug(data)
        return data

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

    def process_dbquestiontags(self, question_identifier, tags):
        """ All tags should exist already in the db """
        for tag in tags:
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

    def process_questions(self, tag):
        logging.debug("Processing questions for " + tag)

        has_more = True
        base_url = self.url + '/2.2/questions?'
        base_url += 'order=desc&sort=activity&site=stackoverflow&key='+self.api_key+'&'
        base_url += 'tagged='+ tag

        # get total number of questions
        url_total = base_url +'&'+'pagesize=1&filter=total'
        data = self._get_api_data(url_total)
        # Hack: total not provided in API as a JSON object
        data = json.loads(data)
        total = data['total']
        logging.info('Total number of questions to download: ' + str(total))

        page = 1
        done = 0
        while has_more:
            questions_ids = [] # used to get answers and comments
            url = base_url + '&' + 'pagesize='+str(self.pagesize)+'&'+'page='+str(page)
            if not self.debug:
                data = self._get_api_data(url)
            else:
                data = StackSampleData.questions

            parser = JSONParser(unicode(data))
            parser.parse()
            # [u'has_more', u'items', u'quota_max', u'quota_remaining']
            data = parser.data['items']
            has_more = parser.data['has_more']
            if self.debug: has_more = False
            page += 1

            for question in data:
                # Each of the question is initialized here
                # [u'is_answered', u'view_count', u'tags', u'last_activity_date', u'answer_count', u'creation_date',
                # u'score', u'link', u'accepted_answer_id', u'owner', u'title', u'question_id']
                dbquestion = Questions()
                if 'user_id' in question['owner']:
                    dbquestion.author_identifier = question['owner']['user_id']
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

                if self.question_new_or_changed(dbquestion):
                    # Question is new or changed
                    self.session.add(dbquestion)
                    self.session.commit()
                    self.process_dbquestiontags(dbquestion.question_identifier, question['tags'])
                    questions_ids.append(question['question_id'])
                    if dbquestion.author_identifier:
                        if dbquestion.author_identifier not in self.user_ids_questions:
                            self.user_ids_questions.append(dbquestion.author_identifier)

                self.total_questions += 1
                done +=1

                if self.total_questions % 10 == 0: logging.info("Done: " + str(done) + "/"+str(total))

            logging.info("Done: " + str(done) + "/"+str(total))

            ids = ";".join([str(x) for x in questions_ids])
            if len(ids)>0:
                # Get all answers for the pagesize questions updated
                self.process_answers(ids)
                # Get all comments for the pagesize questions updated
                self.process_comments(ids)
        return


    def get_search_tags(self):
        found_tags = []

        logging.info("Getting all tags based on: " + self.tags)
        url = self.url + "/2.2/tags?key="+self.api_key+"&"
        url += "order=desc&sort=popular&site=stackoverflow"
        url += "&inname=" + str(self.tags)
        if not self.debug:
            data = self._get_api_data(url)
        else:
            data = StackSampleData.tags

        parser = JSONParser(unicode(data))
        parser.parse()
        tags_data = parser.data['items']
        for tag in tags_data:
            found_tags.append(tag['name'])
        logging.info(found_tags)
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
            logging.debug( "    * Question not found in db")
            found = False
            updated = False

        else:
            # question in db
            question = questions[0]
            # question data from API
            date = datetime.datetime.strptime(dbquestion.last_activity_at, "%Y-%m-%d %H:%M:%S")
            if question.last_activity_at < date:
                #question not updated in db
                logging.debug("    * Question not updated in db")
                updated = False

        return updated, found

    def process_answers(self, dbquestion_ids):
        """ Get all answers for the list of question ids """
        has_more = True
        page = 1
        base_url = self.url + '/2.2/questions/'+str(dbquestion_ids)+'/answers?'
        base_url += 'order=desc&sort=activity&site=stackoverflow&key='+self.api_key
        base_url += '&' + 'pagesize='+str(self.pagesize)
        logging.debug("Getting answers for dbquestion ids" + str(dbquestion_ids))
        dbanswers_ids = []

        while has_more:
            url = base_url + "&page="+str(page)
            if not self.debug:
                data = self._get_api_data(url)
            else:
                has_more = False
                data = StackSampleData.answers

            parser = JSONParser(unicode(data))
            parser.parse()
            # [u'has_more', u'items', u'quota_max', u'quota_remaining']
            has_more = parser.data['has_more']
            page += 1
            data = parser.data['items']

            for answer in data:
                dbanswer = Answers()
                dbanswer.identifier = answer['answer_id']
                dbanswers_ids.append(dbanswer.identifier)
                # dbanswer.body = text
                if 'user_id' in answer['owner']:
                    dbanswer.user_identifier = answer['owner']['user_id']
                    if dbanswer.user_identifier not in self.user_ids_answers:
                        self.user_ids_answers.append(dbanswer.user_identifier)
                dbanswer.question_identifier = answer['question_id']
                create_date = datetime.datetime.fromtimestamp(int(answer['creation_date']))
                dbanswer.submitted_on = create_date.strftime('%Y-%m-%d %H:%M:%S')
                dbanswer.votes = answer['score']

                self.session.add(dbanswer)
                self.total_answers += 1
                self.user_ids_answers.append(dbanswer.user_identifier)
            self.session.commit()
        # Time to get comments for all answers
        while len(dbanswers_ids)>0:
            ids = []
            for i in range(self.pagesize):
                if len(dbanswers_ids)>0:
                    val = dbanswers_ids.pop()
                    if val is not None: ids.append(val)
                    else: logging.info("Found None Answer")
            ids = ";".join([str(x) for x in ids])
            self.process_comments(ids,'answer')

    def process_comments(self, dbpost_ids, kind = 'question'):
        # coments associated to a post (question or answer) that question
        if kind == 'question': base_url = self.url + '/2.2/questions/'
        if kind == 'answer': base_url = self.url + '/2.2/answers/'
        base_url += str(dbpost_ids) +'/comments?'
        base_url += 'order=desc&sort=creation&site=stackoverflow&key='+self.api_key
        base_url += '&' + 'pagesize='+str(self.pagesize)
        logging.debug("Getting comments for " + str(dbpost_ids))
        has_more = True
        page = 1

        while has_more:
            url = base_url + "&page="+str(page)
            if not self.debug:
                data = self._get_api_data(url)
            else:
                data = StackSampleData.comments
                has_more = False

            parser = JSONParser(unicode(data))
            parser.parse()
            # [u'has_more', u'items', u'quota_max', u'quota_remaining']
            if 'has_more' not in parser.data:
                logging.error("No has_more in JSON response. Exiting.")
                print parser.data
                raise
            has_more = parser.data['has_more']
            page += 1
            if 'items' in parser.data:
                data = parser.data['items']
            else:
                logging.error("No items in comments")
                logging.error(parser.data)
                return

            for comment in data:
                dbcomment = Comments()

                # question or answer identifier
                if kind == "question":
                    dbcomment.question_identifier = comment['post_id']
                if kind == "answer":
                    dbcomment.answer_identifier = comment['post_id']
                if 'body' in comment.keys(): dbcomment.body = comment['body']
                if 'user_id' in comment['owner']:
                    dbcomment.user_identifier = comment['owner']['user_id']
                    if dbcomment.user_identifier not in self.user_ids_comments:
                        self.user_ids_comments.append(dbcomment.user_identifier)

                cdate = datetime.datetime.fromtimestamp(int(comment['creation_date']))
                dbcomment.submitted_on = cdate.strftime('%Y-%m-%d %H:%M:%S')

                self.session.add(dbcomment)
                self.total_comments += 1
            self.session.commit()

    def process_users(self, users_ids):
        if users_ids is None: return
        if len(users_ids.split(";"))>self.pagesize:
            logging.error("Max ids overcome in process_users " + users_ids)
            raise Exception
        base_url = self.url + '/2.2/users/'+str(users_ids)+'?'
        base_url += 'order=desc&sort=reputation&site=stackoverflow&key='+self.api_key
        base_url += '&' + 'pagesize='+str(self.pagesize)
        has_more = True
        page = 1

        while has_more:
            url = base_url + "&page="+str(page)
            if not self.debug:
                data = self._get_api_data(url)
            else:
                data = StackSampleData.users
                has_more = False
            parser = JSONParser(unicode(data))
            parser.parse()
            # [u'has_more', u'items', u'quota_max', u'quota_remaining']
            if 'has_more' not in parser.data:
                logging.error("No has_more in JSON response")
                print parser.data
                raise
            has_more = parser.data['has_more']
            data = parser.data['items']

            for user in data:
                dbuser = People()
                dbuser.username = user['display_name']
                dbuser.reputation = user['reputation']
                if 'profile_image' in user:
                    dbuser.avatar = user['profile_image']
                dbuser.last_seen_at = datetime.datetime.fromtimestamp(int(user['last_access_date'])).strftime('%Y-%m-%d %H:%M:%S')
                dbuser.joined_at = datetime.datetime.fromtimestamp(int(user['creation_date'])).strftime('%Y-%m-%d %H:%M:%S')
                dbuser.identifier = user['user_id']
                self.session.add(dbuser)
            self.session.commit()

        return

    def report(self):
        logging.info("Completed.")
        print "Total number of users added " + str(self.total_users)
        print "Total number of questions checked " + str(self.total_questions)
        print "Total number of answers added " + str(self.total_answers)
        print "Total number of comments added " + str(self.total_comments)
        print "Total number of api queries " + str(self.api_queries)

    def parse(self):
        # Initial parsing of general info, users and questions
        tags = self.tags.split(",")

        logging.info("Stack parsing from: " + self.url)

        if len(tags) == 1:
            # If just one tag, we try to find others
            tags = self.get_search_tags()

        for tag in tags:
            # Process questions, answers and comments
            self.process_questions(tag)

        users_id = self.user_ids_questions+self.user_ids_answers
        users_id += self.user_ids_comments
        # Remove duplicates using sets
        users_id = list(set(users_id))
        if self.debug: users_id = StackSampleData.users_ids.split(";")
        self.total_users = len(users_id)

        while len(users_id)>0:
            ids = []
            for i in range(self.pagesize):
                if len(users_id)>0:
                    val = users_id.pop()
                    if val is not None: ids.append(val)
                    else: logging.info("Found None user")
            ids = ";".join([str(x) for x in ids])
            self.process_users(ids)

        self.report()
