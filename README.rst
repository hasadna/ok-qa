open-shot - Open Knesset Question & Answers
===========================================

This repository holds the code for `hasadna`_ project to support open municipal
elections. The code contains a django project for a spcific municipality and 
allows the citizens to ask and upvote questions and for candidates to answer.

You are invited to fork the code, improve the design and send a pull request

.. _hasadna: http://hasadna.org.il

Quick Start - Linux
--------------------

You can access the `dev site`_ or if you're a Django developer, install
it on your local machine::

    $ sudo pip install virtualenvwrapper
    $ mkvirtualenv oshot
    $ git clone https://github.com/hasadna/open-shot.git oshot
    $ cd oshot
    $ pip install -r requirements.txt
    $ python manage.py syncdb --migrate --noinput
    $ python manage.py runserver

.. _dev site: http://oshot.hasadna.org.il



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
    
    
