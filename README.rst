open-shot - Open Knesset Question & Answers
===========================================

This repository holds the code for `localshot`_, a Sadna project to help
voters. The code contains a django project for a spcific municipality and
allows the citizens to ask and upvote questions and for candidates to answer.

You are invited to fork the code, improve the design and send a pull request

.. _localshot: http://localshot.org.il

Quick Start - Linux
--------------------


    $ sudo apt-get install libjpeg-dev
    $ sudo easy_install pip
    $ sudo pip install virtualenv
    $ virtualenv ENV
    $ source ENV/bin/activate
    $ git clone https://github.com/hasadna/open-shot.git
    $ cd open-shot
    $ pip install -r requirements.txt
    $ python manage.py test
    $ python manage.py syncdb --migrate --noinput
    $ python manage.py runserver

You should now be able to access the site at http://localhost:8000

  If you experience problems with avatars, it could be your libjpeg
  is missing. Try to use PNG, and checkout this 
  `answer<http://stackoverflow.com/q/8915296/66595>`_ 

MS Windows
----------

Python setup::

    - Install the latest Python 2.xx` that matching your architecture (32 or 64 bit).
    - Download 'distribute` for your architecture and install it.
    - Open command windows and:
		cd c:\Python27\Scripts
		easy_install pip
		pip install virtualenv
	
Git setup::	

    - Log in or sign in to github
    - Go to the 'Open-Shot' project and Fork it

    - Download and install `GitHub for Windows`_.

    - Run the GitHub program (you should have an icon on the desktop). 
    - Sign in with your username and password.
    - Run `Git Shell` (should have an icon on desktop). 
	
    - In the Git shell create the virtualenv as follows:
        cd C:\
	C:\Python27\Scripts\virtualenv --distribute --system-site-packages hasadna
	cd hasadna
	Scripts\activate
		
    - Clone the project:	
	git clone git@github.com:your-name/open-shot.git oshot
 
    - Sync your local env with the project requirents(this will take some times so have a cup of coffee and relax): 
	pip install -r oshot\requirements.txt 

			If "pip install" worked - then most of the hard work is behind you.
			If "pip install" failed with error message 'hg was not found'
			install 'Mercurial' from http://mercurial.selenic.com/wiki/Download
			and run 'pip install -r oshot\requirements.txt'  again 
			If you have another problem
			Post your error on we will help you fix it.	

Sync the database::

    cd oshot
    python manage.py syncdb --migrate --noinput
    
Activate the local web server::

    python manage.py runserver
    
    
