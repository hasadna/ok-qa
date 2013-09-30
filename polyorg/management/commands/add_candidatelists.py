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
                locality = Entity.objects.get(id=locality)
            except ObjectDoesNotExist:
                print 'list %s locality id %s does not exist' % (list_name, locality)            

            if CandidateList.objects.filter(ballot=ballot).filter(entity=locality).exists():
                print 'list with letters %s exists in %s.' % (ballot, locality.name)
            else:
                candidatelist = CandidateList(name=list_name, ballot=ballot, entity=locality)
                candidatelist.save()

