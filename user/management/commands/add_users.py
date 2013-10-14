# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from user.models import User
from entities.models import Entity

import ucsv as csv


class Command(BaseCommand):
    args = '<members_file>'
    help = 'import members from a csv file'

    def handle(self, *args, **options):
        file_name = args[0]
        f = open(file_name, 'rb')
        d = csv.DictReader(f)
        for row in d:
            username = row['username']

            if User.objects.filter(username=username).exists():
                print 'User %s exists.' % (username)
            else:
                first_name = row.get('first_name', '')
                last_name = row.get('last_name', '')
                email = row.get('email', '')
                locality = row.get('locality', '')
                gender = row.get('gender', '')
                password = row.get('password', '')

                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )

                user.set_password(password)
                user.save()

                user.profile.gender = gender
                try:                    
                    user.profile.locality = Entity.objects.get(id=locality)
                except ObjectDoesNotExist:
                    print 'user %s locality id %s does not exist' % (username, locality)
                user.profile.save()
