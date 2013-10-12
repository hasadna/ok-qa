# -*- coding: utf-8 -*-
import random

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from user.models import User
from polyorg.models import CandidateList, Candidate
from entities.models import Entity

from user.management.commands import ucsv as csv



class Command(BaseCommand):
    args = '<list_file>'
    help = 'import lists from a csv file'

    def handle(self, *args, **options):
        file_name = args[0]
        f = open(file_name, 'rb')
        d = csv.DictReader(f)
        i = 1
        for row in d:
            ordinal = int(row['ordinal'])
            locality_name = row['locality']
            ballot = row['ballot']
            mayor = bool(row['mayor'])
            
            fullname = row['name']

            locality = Entity.objects.filter(division__index=3).get(name_he=locality_name)
            candidatelist = locality.candidatelist_set.get(ballot=ballot)

            last_name, first_name = fullname.split(' ', 1)
            username = u'c_%04d' % i

            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

            password = random.randint(1,99999)
            s = u'%s, %s, %s, %s, %s' % (locality_name, first_name, last_name, username, password)
            print s.encode('utf-8')
            user.set_password(password)
            user.save()

            user.profile.locality = locality
            user.profile.verification = u'V'

            user.profile.save()

            candidate = Candidate(candidate_list=candidatelist, user=user,
                            ordinal=ordinal, for_mayor=mayor)
            candidate.save()

            i += 1

