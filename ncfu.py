#!/usr/bin/env python3

from os import environ

from flask import Flask
from flask_restful import Api
from flask_restful import Resource

from jira import JIRA as Jira


class JiraBot(Resource):
    def fetch_env(self):
        return {
            'svr': environ['JIRA_SERVER_URL'],
            'user': environ['JIRA_USERNAME'],
            'pasw': environ['JIRA_PASSWORD'],
            'origin': environ['JIRA_IN_PROGRESS_COLUMN'],
            'target': environ['JIRA_TODO_COLUMN'],
            'proj_id': environ['JIRA_PROJECT_ID']
        }

    def make_conn(self, svr, user, pasw):
        return Jira(
            { 'server': svr }, basic_auth=(user, pasw)
        )

    def get(self):
        d = self.fetch_env()

        jira = self.make_conn(
            d['svr'], d['user'], d['pasw']
        )

        issues_in_progress = jira.search_issues(
            'project={0} and assignee=currentuser() and status={1}'.format(
                d['proj_id'], d['origin']
            )
        )

        if issues_in_progress:
            for issue in issues_in_progress:
                jira.transition_card(issue, d['target'])


class Warmer(Resource):
    def get(self):
        return 'pong'


app = Flask(__name__)

rest = Api(app)
rest.add_resource(JiraBot, '/work')
rest.add_resource(Warmer, '/ping')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
