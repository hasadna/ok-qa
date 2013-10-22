from __future__ import with_statement
from fabric.api import run, sudo, cd, env, prefix, local
from fabric.contrib.console import confirm

env.hosts = ['localshot.org.il']
env.user = 'oshot'

def loadflatb():
    with cd('~oshot/src/oshot'):
        with prefix('. ENV/bin/activate'):
            run('honcho run python manage.py loaddata fixtures/flatblocks.json')

def dumpflatb():
    local('python manage.py dumpdata -n > fixtures/flatblocks.json')

def refresh(branch='master'):
    local('git push origin ' + branch)
    with cd('~oshot/src/oshot'):
        run('git pull origin ' + branch)
    sudo('restart oshot')
    run("echo 'flush_all' | netcat localhost 11211 -q 1")

def deploy(branch='master'):
    local('git push origin ' + branch)
    with cd('~oshot/src/oshot'):
        run('git pull origin ' + branch)
        with prefix('. ENV/bin/activate'):
            run('pip install -r requirements.txt')
            run('python manage.py test')
            run('honcho run python manage.py syncdb --no-initial-data')
            run('honcho run python manage.py migrate --no-initial-data')
            run('honcho run python manage.py collectstatic --noinput')
    sudo('restart oshot')
    run("echo 'flush_all' | netcat localhost 11211 -q 1")
