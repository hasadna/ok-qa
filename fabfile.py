from __future__ import with_statement
from fabric.api import run, sudo, cd, env, prefix
from fabric.contrib.console import confirm

env.hosts = ['oshot.hasadna.org.il']

def deploy(branch='master'):
    with cd('~oshot/src/oshot'):
        run('git pull origin ' + branch)
        with prefix('. ENV/bin/activate'):
            run('pip install -r requirements.txt')
            run('honcho run python manage.py test')
            run('honcho run python manage.py syncdb --no-initial-data')
            run('honcho run python manage.py migrate --no-initial-data')
            run('honcho run python manage.py collectstatic --noinput')
    sudo('restart oshot')
