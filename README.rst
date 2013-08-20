open-shot - Open Knesset Question & Answers
===========================================

This repository holds the code for `localshot`_ a Sadna project to help
voters. The code contains a django project for a spcific municipality and
allows the citizens to ask and upvote questions and for candidates to answer.

You are invited to fork the code, improve the design and send a pull request

.. _localshot: http://localshot.org.il

Quick Start
-----------

    $ sudo pip install virtualenvwrapper
    $ mkvirtualenv oshot
    $ git clone https://github.com/hasadna/open-shot.git
    $ cd open-shot
    $ cp .env.dev .env
    $ pip install -r requirements.txt
    $ python manage.py syncdb --migrate
    $ honcho start

You should now be able to access the site at http://localhost:8000
