# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from polyorg.models import CandidateList
from entities.models import Entity

from user.management.commands import ucsv as csv


class Command(BaseCommand):
    args = '<list_file>'
    help = 'import lists from a csv file'

    def handle(self, *args, **options):
        file_name = args[0]
        f = open(file_name, 'rb')
        d = csv.DictReader(f)
        for row in d:
            list_name = row.get('list_name','')
            locality = row.get('locality', '')
            ballot = row.get('ballot','')
            try:
                locality = Entity.objects.filter(division__index=3).get(name_he=locality)
            except:
                print locality
            try: 
                candidatelist = locality.candidatelist_set.get(ballot=ballot)
                candidatelist.name = list_name
            except:
                candidatelist = CandidateList(name=list_name, ballot=ballot, entity=locality)
            candidatelist.save()

