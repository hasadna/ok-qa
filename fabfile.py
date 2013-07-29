from fabric.api import local

def deploy_party(party, collectstatic):
    run('cd src/oshot')
    run('git pull origin master')
    run('workon oshot')
    run('pip install -r requirments.txt')
    run('python manage.py syncdb --migrate')
    run('python manage.py --noinput collectstatic')
    sudo('reload oshot')

def runserver():
    local('python manage.py collectstatic --noinput')
    local('python manage.py runserver')
