# Upkarma

Upkarma is a Twitter *game*
initially created for the Lithuanian Twitter community.

The game is coded in Python using Django and Django REST Framework.
PostgreSQL and Redis are used for storage.

## Premise

The game allows you to award a person for an interesting tweet
by tagging the person in a tweet like this:

    #upkarma 5 @JohnSmith thanks for the article!

where `5` indicates the amount of points to give.

The points are tallied up on the website,
but have no inherent meaning or value
and can not be used for anything.

[My instance of Upkarma](https://upkarma.lt/) has been running since 2013.

## Components

* `karma/bot` is the bot that uses Twitter search and streaming APIs
  to look for new tweets with the game's hashtag.
* `karma/bot/management` contains a command for starting the aforementioned bot
  and another one to update the cached user avatar URLs.
* `karma/importer` was used to migrate the existing data
  from an earlier hacked-together version of Upkarma.
* `karma/news` is a simple news app.
  I coded it because I like rolling my own stuff.
* There is an Twitter OAuth based login mechanism,
  but I never got around to implementing any additional features
  you would get when logged in.

## Disclaimers

* I wrote most of this code when I was 18.
  As such, the repo is full of both brilliant and horrible code.
  Take inspiration at your own risk.
* While this is a pretty standard Django project,
  there are no installation instructions.
  However, the code itself is documented
  and might have some educational value.
* This repository does not include the frontend templates and styles
  as I am pretty sure I took the Bootstrap template
  from a website that did not allow for redistribution of modifications.
* User-facing messages are hardcoded in Lithuanian. Sorry.
* If you do run your own instance,
  please do not use `#upkarma` as the hashtag.
  It can only end in pain for both of us.
