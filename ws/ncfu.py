#!/usr/bin/env python3

'''This is the logic that powers no-candy-for-u.'''


import traceback
from os import environ

from flask import Flask
from flask_restful import Api
from flask_restful import Resource

from jira import JIRA as Jira


class JiraBot(Resource):
    '''Connects with Jira and performs the appropriate actions.

    Here is where the magic happens. This handler can connect to Jira with
    basic authentication (i.e., with username and password), search for issues
    in a given criteria and move those. It's the heart of the operation that
    powers the whole thing.
    '''

    def fetch_env(self):
        '''Makes all the environment variables needed accessible.

        Returns:
            dict: A dictionary containing the Jira server URL, the account
                  username, the password, project / board id and the columns
                  identifications of the kanban.
        '''
        return {
            'svr': environ['JIRA_SERVER_URL'],
            'user': environ['JIRA_USERNAME'],
            'pasw': environ['JIRA_PASSWORD'],
            'origin': environ['JIRA_IN_PROGRESS_COLUMN'],
            'target': environ['JIRA_TODO_COLUMN'],
            'proj_id': environ['JIRA_PROJECT_ID']
        }

    def make_conn(self, svr, user, pasw):
        '''Connects to Jira via basic authentication.

        Returns:
            object: The Jira connection.
        '''
        return Jira(
            { 'server': svr }, basic_auth=(user, pasw)
        )

    def get(self):
        '''The GET method handler.

        When this method is invoked, the application connects to Jira and
        performs a search with three important criterias: the project id (in
        which project should the webservice acts upon), the issue assignee and
        it's current status. In other words: if there's any issue on a X kanban
        board that belongs to me and it's current status is "in progress",
        please show me.

        if has any, the issue is transitioned from "in progress" to "todo" and
        the action is "saved" for further response.

        The OK response (200) will necessarily have a key named "forgot" that
        indicates if any issue were left behind (and had been moved). In the
        case of something being forgotten, the response will also contain the
        issue key, as well the title/summary.

        On the event of any exception, the traceback will be recorded and sent
        as the response.

        Returns:
            tuple: A dictionary with an appropriate response for the execution
                   of the method, the HTTP response code.
        '''
        try:
            d = self.fetch_env()

            jira = self.make_conn(
                d['svr'], d['user'], d['pasw']
            )

            issues_in_progress = jira.search_issues(
                'project={0} and assignee=currentuser() and status="{1}"'.format(
                    d['proj_id'], d['origin']
                )
            )

            left_behind = []
            if issues_in_progress:
                for issue in issues_in_progress:
                    left_behind.append({
                        'key': issue.key,
                        'title': issue.fields.summary
                    })
                    jira.transition_issue(issue, d['target'])

                return {
                    'forgot': 1,
                    'leftBehind': left_behind
                }, 200

            else:
                return {
                    'forgot': 0
                }, 200

        except Exception:
            return {
                'traceback': traceback.format_exc()
            }, 500


class Warmer(Resource):
    '''The "keep warm" resource handler.

    Heroku is known to put your live applications in an "asleep mode" after 30
    minutes of inactivity. This is a mechanism desgined to save CPU and RAM
    usage, specially in free accounts. When the service is in this mode, new
    requests tends to require more time to be processed, since Heroku will need
    to "awake" your application.

    This handler provides a simple way to ping to this web service, which then
    can ensures that Heroku will keep the service awaken/warm. Everytime it
    receives a GET request to '/ping', it will respond with a 'pong'. That's
    all it takes to keep up and running all the time.

    This workaround is not automagic and requires that someone will ping this
    web service from time to time.
    '''

    def get(self):
        '''The GET method handler.

        Returns:
            string: The ping response, which is a pong.
        '''
        return 'pong', 200


# The flask object.
app = Flask(__name__)

# The resource / handler binder.
# Specifies a handler class to each resource/route.
rest = Api(app)
rest.add_resource(JiraBot, '/work')
rest.add_resource(Warmer, '/ping')


if __name__ == '__main__':
    # The application entrypoint. Only needed for local execution.
    app.run(host='0.0.0.0', port=8080)
