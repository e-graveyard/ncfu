/**
 * @project no-candy-for-u (ncfu)
 * @author Caian R. Ertl
 * @license MIT
 * @repository https://github.com/caianrais/ncfu
 */


// The web service endpoint/url
var WS_URL = 'https://your-app-here.herokuapp.com/';


/**
 * Pauses the execution
 *
 * Interrupts the routine execution for a given number of seconds
 *
 * @param {Integer} secs - The number of seconds
 */
function wait(secs) {
    Utilities.sleep(secs * 1000);
}

/**
 * Consumes the web service
 *
 * Makes a GET request to the web service in a given resource name
 *
 * @param {String} resource - The resource name
 * @return {Object} The webservice response
 */
function consume(resource) {
    return UrlFetchApp.fetch(WS_URL.concat(resource));
}

/**
 * Notifies an event via email
 *
 * Sends an email message when an event occurs, i.e. the transition of an issue
 * from "in progress" to "todo" or an uncaught exception on the web service.
 *
 * @param {String} status - The status of the event.
 * @param {Object} content - The object containing context information about the event.
 */
function notify(status, content) {

    var msg = '<b>$MSG</b><br/>Here\'s what:<br/><br/><ul>';

    if (status == 'ok') {
        msg = msg.replace(
            '$MSG', 'You forgot to move some issues on Jira, but i got you buddy.'
        );

        for (var i = 0; i < content.length; i++) {
            msg = msg
                .concat('<li>($KEY) - $TITLE</li>')
                .replace('$KEY', content[i].key)
                .replace('$TITLE', content[i].title);
        }

    }
    else {
        msg = msg.replace(
            '$MSG', 'I\'ve tried to save your skin this night but something went terribly wrong.'
        );

        for (var i = 0; i < content.length; i++) {
            msg = msg
                .concat('<li>(at line $LINE) $MESSAGE</li>')
                .replace('$LINE', content[i].line)
                .replace('$MESSAGE', content[i].message);
        }
    }

    msg = msg.concat('</ul>');
    msg = HtmlService.createTemplate(msg).evaluate().getContent();

    MailApp.sendEmail({
        to: 'name@domain.com',
        subject: 'NCFU Report',
        htmlBody: msg
    });

}

/**
 * Triggers the web service
 *
 * Sends a GET request to the '/work' resource. If one or more issue were left
 * behind, the user will be notified. If something went wrong, the function will
 * retry three times, with 30 seconds intervals. If it continues to fail, the user
 * will be notified as well.
 */
function activate() {

    var retry   = 3,
        success = false,
        errors  = [];

    while (retry > 0) {
        try {
            var res = JSON.parse(consume('work'));
            if (res.forgot) {
                notify('ok', res.leftBehind);
            }

            success = true;
            break;
        }
        catch(err) {
            errors.push({
                message: err.message,
                line: err.lineNumber
            });

            retry -= 1;
            wait(30);
        }
    }

    if (!success)
        notify('error', errors);

}

/**
 * Pings the web service
 *
 * Sends a GET request to the '/ping' resource in order to maintain the heroku
 * service "warm" (since it's tend to sleep after 30 min or so).
 */
function warm() {
    consume('ping');
}
