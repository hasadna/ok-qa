open-shot - Open Knesset Question & Answers
===========================================

This repository holds the code for `localshot`_, a Sadna project to help
voters. The code contains a Django project for a specific municipality and
allows the citizens to ask and up-vote questions and for candidates to answer.

You are invited to fork the code, improve the design and send a pull request

.. _localshot: http://localshot.org.il

Quick Start - Linux
--------------------

::

    $ sudo apt-get install python3-venv
    $ python3 -m venv env
    $ . env/bin/activate
    $ pip install -r requirments.txt
    $ pip install --upgrade pip
    $ python manage.py migrate
    $ python manage.py createsuperuser
    ...
    $ python manage.py runserver

You should now be able to access the site at http://localhost:8000
and the admin interface at /admin.

