# ncfu: No Candy For U!

![No Candy For U](docs/icon.png)

## About

`ncfu` **(No Candy For U)** is a tiny service composed by two web services: a
live application that sits on Heroku and a "cron job"-like script on Google
Apps Script. It can automatically move Jira issues from one status to another
(i.e., without human interaction), saving you some pennies.

Though it was write for Jira in mind, it can be easily ported to deal with
Trello and other project management applications.


## Motivation

At work, we have an "internal practice" that consists in paying with candies
and other delies whenever someone forgets to change the status of an issue
inside Jira. Say, if you're working on something, stops and forgets to change
the status of that something (from "in progress" to "todo" or even "done"),
you'll be quickly prompted to "pay". **And the payment is made with candies.**

This work of genius was made so I never ever have to pay anymore (*wink wink*).


## Structure

There's two directories that matters in this repository:

 - `as`: **(Apps Script)** The Google Apps Script "cron job".
 - `ws`: **(Web Service)** The Flask web service that deals with Jira.


### The web service

This is the heart of the operation. It's a Flask application that connects to
Jira, searches for occurrences of forgotten issues and do the transitions
between states. It was "designed" for Heroku, though you can easily hack around
and made it compatible with AWS Lambda and such.


### The "cron job"

This is what fires the Flask application and ensures the service is always warm
and ready-to-go. It uses Google Apps Script for three simple reasons: Apps
Script is free, it nicely integrates with other Google services, like Gmail,
and because it have time-driven triggers (which mean I can define daily or
hourly triggers that spawns the functions, which then spawn the Flask
application... more or less like a cron job).


## Usage

I know you're reading, Marcio. **No no no...**
