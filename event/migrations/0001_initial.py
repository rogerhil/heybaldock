# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table('event_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('complement', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('country', self.gf('django.db.models.fields.CharField')(default='Brazil', max_length=128)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('phone1', self.gf('django.db.models.fields.IntegerField')()),
            ('phone2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('phone3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('event', ['Location'])

        # Adding model 'Event'
        db.create_table('event_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('starts_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('ends_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Location'])),
        ))
        db.send_create_signal('event', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table('event_location')

        # Deleting model 'Event'
        db.delete_table('event_event')


    models = {
        'event.event': {
            'Meta': {'object_name': 'Event'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'ends_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['event.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'starts_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'event.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'Brazil'", 'max_length': '128'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'phone1': ('django.db.models.fields.IntegerField', [], {}),
            'phone2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'phone3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        }
    }

    complete_apps = ['event']