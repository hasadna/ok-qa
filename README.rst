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

    $ sudo apt-get install git-core mercurial python2.7-dev python-setuptools libjpeg-dev
    $ sudo easy_install pip
    $ sudo pip install virtualenv
    $ git clone https://github.com/hasadna/open-shot.git
    $ cd open-shot
    $ virtualenv -p /usr/bin/python2.7 ENV
    $ source ENV/bin/activate
    $ pip install -r requirements.txt
    $ python manage.py test
    $ python manage.py syncdb --migrate --noinput
    $ python manage.py runserver

You should now be able to access the site at http://localhost:8000

  If you experience problems with avatars, it could be your libjpeg
  is missing. Try to use PNG, and checkout this 
  `answer <http://stackoverflow.com/q/8915296/66595>`_.

MS Windows
----------

Python setup:

1) Install the latest Python 2.xx` that matching your architecture (32 or 64 bit).
2) Download 'distribute` for your architecture and install it.
3) Open command windows and::

     cd c:\Python27\Scripts
     easy_install pip
     pip install virtualenv

Git setup:

1) Log in or sign in to github
2) Go to the 'Open-Shot' project and Fork it
3) Download and install `GitHub for Windows`_.
4) Run the GitHub program (you should have an icon on the desktop).
5) Sign in with your username and password.
6) Run `Git Shell` (should have an icon on desktop).
7) In the Git shell create the virtualenv as follows::

     cd C:\
     C:\Python27\Scripts\virtualenv --distribute --system-site-packages hasadna
     cd hasadna
     Scripts\activate

8) Clone the project::

	git clone git@github.com:your-name/open-shot.git oshot

9) Sync your local env with the project requirements (this will take some times so have a cup of coffee and relax)::

	pip install -r oshot\requirements.txt 

.. _Github for Windows: http://windows.github.com/

Troubleshooting:

- If "pip install" worked -- then most of the hard work is behind you.
- If "pip install" failed with error message 'hg was not found'::

    install 'Mercurial' from http://mercurial.selenic.com/wiki/Download
    and then
    run 'pip install -r oshot\requirements.txt' again

- If you have another problem, post your error and we will help you fix it.

Sync the database::

    cd oshot
    python manage.py syncdb --migrate --noinput
    
Activate the local web server::

    python manage.py runserver
    
    
