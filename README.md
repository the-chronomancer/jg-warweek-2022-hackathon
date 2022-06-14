# JG Wellness 2.0 AKA EffingLegs

![sweep the leg](https://github.com/the-chronomancer/jg-warweek-2022-hackathon/blob/master/cobra_kai.jpeg)

## Why do I need this?

It's Tuesday and you're walking into the best office on the planet:
JG HQ.

Huh - the elevator - how silly. I think I'll take the stairs!

*huff* *huff* *puff* *wheeeew*

Made it up five whole flights, ahh look at that nice sign reminding me
to log my stairs activity - haha yep I'll be forgetting to do that
almost immediately once I sit down and become consumed with client work.

If only there was a way to log my stair climbing efforts where I had
to do no logging on my own and they just got tallied up somewhere in the cloud
... automagically. Seems like a pipe dream... or is it?

## Wat do?

JG EffingLegs takes your traditional stair logging workflow to the
next level of awesome. Logging your stairs no longer needs to be done
in a web browser with your smart device or at your desk once you're done
climbing.

Forgetting how many flights you climbed no longer is an issue.

JG EffingLegs uses that wonderful face of yours, and it's kinda
hard to forget that no matter how late you were staying up bashing
the cron the night before.

The Velominati crew has taken it upon themselves to import high
quality headshots of all JG employees (~96 or so as of 3/4/2022)
into Amazon for usage within their Rekognition API. Anyone
can begin logging stair efforts using our prototype and their
wonderful face.

## What's next for EffingLegs

* Challenge other JGers to a stair-off for any time period over a day
* Oauth2 integration
* Deploy protoype to RaspPi or other low-cost hardware with USB camera and physical button/gpio
* Add more metrics and reports so JGers can dive into past performance
* Allow JGers to add additional headshots to increase accuracy of AI or support that killer new beard
* Sweep the Legs
* Scheduled jobs to compile aggregate challenge/climb data for management
* Add a dev environment

## What's the stack?

This is a lightweight Web 2 stack using React and AWS SAM.

The stack can be easily developed and tested locally.

For persistence we're using an RDS/PostgreSQL cluster to store users
and their stair climbing achievements ingested from the IoT edge.

Functional / smoke testing is provided by Nightwatch.js
to ensure basic functionality exists before shipping
the app out automatically. Upon deploy to `prod` we
have functional tests wired in to ensure the site
can be navigated to and is responsive.

## How to I hack on this?

You'll need AWS SAM, Node.js 16.x and Python 3.9 installed locally before getting
started with this.

To start the Angular webclient:

```bash
# optional
sudo npm install -g yarn
# required
cd client
npm install
yarn install
yarn start
# navigate to http://localhost:3000 and enjoy!
```

To start the Python API locally:

```bash
sam build (--use-container, maybe?)
sam local start-api
```

## CI/CD

This application utilizes GitHub Actions and a mixture of custom
and pre-made workflows from vendors like Amazon.

CI/CD pipelines are located within the `.github/workflows` folder.

## SQL Schema

The database Schema is relatively simple, we have four tables
that currently track users, their efforts, and challenges
between users. We also have a table to link users and their challenges.

SQL seed entries can be found in the `sql` folder of this project.
