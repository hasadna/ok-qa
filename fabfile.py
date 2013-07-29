from __future__ import with_statement
from fabric.api import run, sudo, cd, env, prefix
from fabric.contrib.console import confirm

env.hosts = ['oshot.hasadna.org.il']

def deploy():
    with cd('~oshot/src/open-shot'):
        run('git pull origin master')
        with prefix('. ~oshot/.virtualenvs/oshot/bin/activate'):
            run('pip install -r requirements.txt')
            result = sudo('stop oshot')
            run('honcho run python manage.py test')
            run('honcho run python manage.py syncdb --migrate')
            run('honcho run python manage.py --noinput collectstatic')
    sudo('start oshot')
