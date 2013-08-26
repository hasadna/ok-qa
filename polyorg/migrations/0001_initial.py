# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CandidateList'
        db.create_table(u'polyorg_candidatelist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('ballot', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('number_of_seats', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('surplus_partner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['polyorg.CandidateList'], null=True, blank=True)),
            ('mpg_html_report', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('img_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('youtube_user', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('wikipedia_page', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('twitter_account', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('facebook_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('platform', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'polyorg', ['CandidateList'])

        # Adding model 'Party'
        db.create_table(u'polyorg_party', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('accepts_memberships', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'polyorg', ['Party'])

        # Adding model 'Candidate'
        db.create_table(u'polyorg_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('candidate_list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['polyorg.CandidateList'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['polyorg.Party'], null=True, blank=True)),
            ('votes', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='S', max_length=1)),
        ))
        db.send_create_signal(u'polyorg', ['Candidate'])


    def backwards(self, orm):
        # Deleting model 'CandidateList'
        db.delete_table(u'polyorg_candidatelist')

        # Deleting model 'Party'
        db.delete_table(u'polyorg_party')

        # Deleting model 'Candidate'
        db.delete_table(u'polyorg_candidate')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'polyorg.candidate': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Candidate'},
            'candidate_list': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['polyorg.CandidateList']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['polyorg.Party']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'votes': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'polyorg.candidatelist': {
            'Meta': {'object_name': 'CandidateList'},
            'ballot': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'candidates': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'through': u"orm['polyorg.Candidate']", 'blank': 'True'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'mpg_html_report': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'number_of_seats': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'platform': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'surplus_partner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['polyorg.CandidateList']", 'null': 'True', 'blank': 'True'}),
            'twitter_account': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'wikipedia_page': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'youtube_user': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        u'polyorg.party': {
            'Meta': {'object_name': 'Party'},
            'accepts_memberships': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['polyorg']