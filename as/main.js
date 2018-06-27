var WS_URL = 'https://your-app-here.herokuapp.com/';


/**
 *
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
 *
 */
function wait(secs) {
    Utilities.sleep(secs * 1000);
}

/**
 *
 */
function consume(resource) {
    return UrlFetchApp.fetch(WS_URL.concat(resource));
}

/**
 *
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
 *
 */
function warm() {
    consume('ping');
}
