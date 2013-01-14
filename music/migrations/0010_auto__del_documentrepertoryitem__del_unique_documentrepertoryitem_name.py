# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Repertory', fields ['name', 'event']
        db.delete_unique('music_repertory', ['name', 'event_id'])

        # Removing unique constraint on 'PlayerRepertoryItemRating', fields ['user', 'player_repertory_item']
        db.delete_unique('music_playerrepertoryitemrating', ['user_id', 'player_repertory_item_id'])

        # Removing unique constraint on 'UserRepertoryItemRating', fields ['user', 'repertory_item']
        db.delete_unique('music_userrepertoryitemrating', ['user_id', 'repertory_item_id'])

        # Removing unique constraint on 'MusicAudioSegment', fields ['name', 'player_repertory_item']
        db.delete_unique('music_musicaudiosegment', ['name', 'player_repertory_item_id'])

        # Removing unique constraint on 'DocumentPlayerRepertoryItem', fields ['name', 'player_repertory_item']
        db.delete_unique('music_documentplayerrepertoryitem', ['name', 'player_repertory_item_id'])

        # Removing unique constraint on 'RepertoryGroup', fields ['repertory', 'order']
        db.delete_unique('music_repertorygroup', ['repertory_id', 'order'])

        # Removing unique constraint on 'MusicScoreSegment', fields ['name', 'player_repertory_item']
        db.delete_unique('music_musicscoresegment', ['name', 'player_repertory_item_id'])

        # Removing unique constraint on 'PlayerRepertoryItem', fields ['player', 'repertory_item']
        db.delete_unique('music_playerrepertoryitem', ['player_id', 'repertory_item_id'])

        # Removing unique constraint on 'RepertoryGroupItem', fields ['group', 'number']
        db.delete_unique('music_repertorygroupitem', ['group_id', 'number'])

        # Removing unique constraint on 'RepertoryGroupItem', fields ['song', 'group']
        db.delete_unique('music_repertorygroupitem', ['song_id', 'group_id'])

        # Removing unique constraint on 'DocumentRepertoryItem', fields ['name', 'repertory_item']
        db.delete_unique('music_documentrepertoryitem', ['name', 'repertory_item_id'])

        # Deleting model 'DocumentRepertoryItem'
        db.delete_table('music_documentrepertoryitem')

        # Deleting model 'RepertoryGroupItem'
        db.delete_table('music_repertorygroupitem')

        # Deleting model 'PlayerRepertoryItem'
        db.delete_table('music_playerrepertoryitem')

        # Removing M2M table for field tag_types on 'PlayerRepertoryItem'
        db.delete_table('music_playerrepertoryitem_tag_types')

        # Deleting model 'MusicScoreSegment'
        db.delete_table('music_musicscoresegment')

        # Deleting model 'RepertoryGroup'
        db.delete_table('music_repertorygroup')

        # Deleting model 'DocumentPlayerRepertoryItem'
        db.delete_table('music_documentplayerrepertoryitem')

        # Deleting model 'VideoPlayerRepertoryItem'
        db.delete_table('music_videoplayerrepertoryitem')

        # Deleting model 'MusicAudioSegment'
        db.delete_table('music_musicaudiosegment')

        # Deleting model 'UserRepertoryItemRating'
        db.delete_table('music_userrepertoryitemrating')

        # Deleting model 'PlayerRepertoryItemRating'
        db.delete_table('music_playerrepertoryitemrating')

        # Deleting model 'VideoRepertoryItem'
        db.delete_table('music_videorepertoryitem')

        # Adding model 'RepertoryItem'
        db.create_table('music_repertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Song'])),
            ('repertory', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['music.Repertory'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tempo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('tonality', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
        ))
        db.send_create_signal('music', ['RepertoryItem'])

        # Adding unique constraint on 'RepertoryItem', fields ['song', 'repertory']
        db.create_unique('music_repertoryitem', ['song_id', 'repertory_id'])

        # Adding model 'PlayerEventRepertory'
        db.create_table('music_playereventrepertory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='event_repertories', null=True, to=orm['music.Player'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.EventRepertoryItem'])),
        ))
        db.send_create_signal('music', ['PlayerEventRepertory'])

        # Adding unique constraint on 'PlayerEventRepertory', fields ['player', 'item']
        db.create_unique('music_playereventrepertory', ['player_id', 'item_id'])

        # Adding model 'EventRepertoryItem'
        db.create_table('music_eventrepertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repertory', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['music.EventRepertory'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events_items', to=orm['music.RepertoryItem'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('music', ['EventRepertoryItem'])

        # Adding unique constraint on 'EventRepertoryItem', fields ['repertory', 'item']
        db.create_unique('music_eventrepertoryitem', ['repertory_id', 'item_id'])

        # Adding model 'EventRepertory'
        db.create_table('music_eventrepertory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Event'])),
            ('user_lock', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='event_repertories', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('music', ['EventRepertory'])

        # Deleting field 'Repertory.description'
        db.delete_column('music_repertory', 'description')

        # Deleting field 'Repertory.name'
        db.delete_column('music_repertory', 'name')

        # Deleting field 'Repertory.event'
        db.delete_column('music_repertory', 'event_id')


        # Changing field 'Repertory.band'
        db.alter_column('music_repertory', 'band_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, null=True, to=orm['music.Band']))
        # Adding unique constraint on 'Repertory', fields ['band']
        db.create_unique('music_repertory', ['band_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Repertory', fields ['band']
        db.delete_unique('music_repertory', ['band_id'])

        # Removing unique constraint on 'EventRepertoryItem', fields ['repertory', 'item']
        db.delete_unique('music_eventrepertoryitem', ['repertory_id', 'item_id'])

        # Removing unique constraint on 'PlayerEventRepertory', fields ['player', 'item']
        db.delete_unique('music_playereventrepertory', ['player_id', 'item_id'])

        # Removing unique constraint on 'RepertoryItem', fields ['song', 'repertory']
        db.delete_unique('music_repertoryitem', ['song_id', 'repertory_id'])

        # Adding model 'DocumentRepertoryItem'
        db.create_table('music_documentrepertoryitem', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.RepertoryGroupItem'])),
            ('document', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('music', ['DocumentRepertoryItem'])

        # Adding unique constraint on 'DocumentRepertoryItem', fields ['name', 'repertory_item']
        db.create_unique('music_documentrepertoryitem', ['name', 'repertory_item_id'])

        # Adding model 'RepertoryGroupItem'
        db.create_table('music_repertorygroupitem', (
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['music.RepertoryGroup'])),
            ('mode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Song'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('tonality', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('tempo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['RepertoryGroupItem'])

        # Adding unique constraint on 'RepertoryGroupItem', fields ['song', 'group']
        db.create_unique('music_repertorygroupitem', ['song_id', 'group_id'])

        # Adding unique constraint on 'RepertoryGroupItem', fields ['group', 'number']
        db.create_unique('music_repertorygroupitem', ['group_id', 'number'])

        # Adding model 'PlayerRepertoryItem'
        db.create_table('music_playerrepertoryitem', (
            ('as_member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Artist'], null=True, blank=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(related_name='repertory_items', null=True, to=orm['music.Player'], blank=True)),
            ('is_lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='players', to=orm['music.RepertoryGroupItem'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('music', ['PlayerRepertoryItem'])

        # Adding M2M table for field tag_types on 'PlayerRepertoryItem'
        db.create_table('music_playerrepertoryitem_tag_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('playerrepertoryitem', models.ForeignKey(orm['music.playerrepertoryitem'], null=False)),
            ('instrumenttagtype', models.ForeignKey(orm['music.instrumenttagtype'], null=False))
        ))
        db.create_unique('music_playerrepertoryitem_tag_types', ['playerrepertoryitem_id', 'instrumenttagtype_id'])

        # Adding unique constraint on 'PlayerRepertoryItem', fields ['player', 'repertory_item']
        db.create_unique('music_playerrepertoryitem', ['player_id', 'repertory_item_id'])

        # Adding model 'MusicScoreSegment'
        db.create_table('music_musicscoresegment', (
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('score', self.gf('lib.fields.JSONField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('music', ['MusicScoreSegment'])

        # Adding unique constraint on 'MusicScoreSegment', fields ['name', 'player_repertory_item']
        db.create_unique('music_musicscoresegment', ['name', 'player_repertory_item_id'])

        # Adding model 'RepertoryGroup'
        db.create_table('music_repertorygroup', (
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('repertory', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groups', to=orm['music.Repertory'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('music', ['RepertoryGroup'])

        # Adding unique constraint on 'RepertoryGroup', fields ['repertory', 'order']
        db.create_unique('music_repertorygroup', ['repertory_id', 'order'])

        # Adding model 'DocumentPlayerRepertoryItem'
        db.create_table('music_documentplayerrepertoryitem', (
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['music.PlayerRepertoryItem'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('document', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.SmallIntegerField')(default=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('music', ['DocumentPlayerRepertoryItem'])

        # Adding unique constraint on 'DocumentPlayerRepertoryItem', fields ['name', 'player_repertory_item']
        db.create_unique('music_documentplayerrepertoryitem', ['name', 'player_repertory_item_id'])

        # Adding model 'VideoPlayerRepertoryItem'
        db.create_table('music_videoplayerrepertoryitem', (
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('thumbnail_small', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('recorded', self.gf('django.db.models.fields.DateField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
        ))
        db.send_create_signal('music', ['VideoPlayerRepertoryItem'])

        # Adding model 'MusicAudioSegment'
        db.create_table('music_musicaudiosegment', (
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('audio', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('music', ['MusicAudioSegment'])

        # Adding unique constraint on 'MusicAudioSegment', fields ['name', 'player_repertory_item']
        db.create_unique('music_musicaudiosegment', ['name', 'player_repertory_item_id'])

        # Adding model 'UserRepertoryItemRating'
        db.create_table('music_userrepertoryitemrating', (
            ('rate', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users_ratings', to=orm['music.RepertoryGroupItem'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='repertory_items_ratings', to=orm['auth.User'])),
        ))
        db.send_create_signal('music', ['UserRepertoryItemRating'])

        # Adding unique constraint on 'UserRepertoryItemRating', fields ['user', 'repertory_item']
        db.create_unique('music_userrepertoryitemrating', ['user_id', 'repertory_item_id'])

        # Adding model 'PlayerRepertoryItemRating'
        db.create_table('music_playerrepertoryitemrating', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_repertory_items_ratings', to=orm['auth.User'])),
            ('rate', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users_ratings', to=orm['music.PlayerRepertoryItem'])),
        ))
        db.send_create_signal('music', ['PlayerRepertoryItemRating'])

        # Adding unique constraint on 'PlayerRepertoryItemRating', fields ['user', 'player_repertory_item']
        db.create_unique('music_playerrepertoryitemrating', ['user_id', 'player_repertory_item_id'])

        # Adding model 'VideoRepertoryItem'
        db.create_table('music_videorepertoryitem', (
            ('repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('thumbnail_small', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('recorded', self.gf('django.db.models.fields.DateField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('music', ['VideoRepertoryItem'])

        # Deleting model 'RepertoryItem'
        db.delete_table('music_repertoryitem')

        # Deleting model 'PlayerEventRepertory'
        db.delete_table('music_playereventrepertory')

        # Deleting model 'EventRepertoryItem'
        db.delete_table('music_eventrepertoryitem')

        # Deleting model 'EventRepertory'
        db.delete_table('music_eventrepertory')

        # Adding field 'Repertory.description'
        db.add_column('music_repertory', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Repertory.name'
        raise RuntimeError("Cannot reverse this migration. 'Repertory.name' and its values cannot be restored.")
        # Adding field 'Repertory.event'
        db.add_column('music_repertory', 'event',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Event'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'Repertory.band'
        db.alter_column('music_repertory', 'band_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Band'], null=True))
        # Adding unique constraint on 'Repertory', fields ['name', 'event']
        db.create_unique('music_repertory', ['name', 'event_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photo.PhotoAlbum']", 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'complement': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'Brazil'", 'max_length': '128'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'location_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone3': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'music.album': {
            'Meta': {'unique_together': "(('name', 'artist'),)", 'object_name': 'Album'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'albums'", 'to': "orm['music.Artist']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.AlbumGenre']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('lib.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'style': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.AlbumStyle']", 'symmetrical': 'False'}),
            'thumb': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'music.albumcover': {
            'Meta': {'object_name': 'AlbumCover'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Album']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Size']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.ImageType']", 'null': 'True', 'blank': 'True'})
        },
        'music.albumgenre': {
            'Meta': {'object_name': 'AlbumGenre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.albumstyle': {
            'Meta': {'object_name': 'AlbumStyle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.artist': {
            'Meta': {'object_name': 'Artist'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'active_members_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'albums_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'discogs_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'inactive_members_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'is_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'membership': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.Artist']", 'through': "orm['music.ArtistMembership']", 'symmetrical': 'False'}),
            'metadata': ('lib.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.artistimage': {
            'Meta': {'object_name': 'ArtistImage'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['music.Artist']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Size']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.ImageType']", 'null': 'True', 'blank': 'True'})
        },
        'music.artistmembership': {
            'Meta': {'object_name': 'ArtistMembership'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['music.Artist']"}),
            'date_joined': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['music.Artist']"})
        },
        'music.band': {
            'Meta': {'object_name': 'Band'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.Artist']", 'through': "orm['music.BandArtist']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'enable_inactive_members': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bands'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'music.bandartist': {
            'Meta': {'unique_together': "(('band', 'artist'),)", 'object_name': 'BandArtist'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bands'", 'to': "orm['music.Artist']"}),
            'band': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Band']"}),
            'enable_inactive_artist_members': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'music.composer': {
            'Meta': {'object_name': 'Composer'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'discogs_resource_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('lib.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.composerrole': {
            'Meta': {'unique_together': "(('role', 'composer'),)", 'object_name': 'ComposerRole'},
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Composer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'music.eventrepertory': {
            'Meta': {'object_name': 'EventRepertory'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['event.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_lock': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'event_repertories'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'music.eventrepertoryitem': {
            'Meta': {'unique_together': "(('repertory', 'item'),)", 'object_name': 'EventRepertoryItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events_items'", 'to': "orm['music.RepertoryItem']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'repertory': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['music.EventRepertory']"})
        },
        'music.imagetype': {
            'Meta': {'object_name': 'ImageType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.instrumenttagtype': {
            'Meta': {'unique_together': "(('name', 'instrument'), ('level', 'instrument'))", 'object_name': 'InstrumentTagType'},
            'friendly_name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tag_types'", 'to': "orm['music.Instrument']"}),
            'level': ('django.db.models.fields.SmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'music.musichistorychanges': {
            'Meta': {'object_name': 'MusicHistoryChanges'},
            'content': ('lib.fields.PickleField', [], {'default': "''"}),
            'content_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'music_history'", 'to': "orm['auth.User']"})
        },
        'music.player': {
            'Meta': {'unique_together': "(('instrument', 'user'),)", 'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'to': "orm['music.Instrument']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instruments'", 'to': "orm['auth.User']"})
        },
        'music.playereventrepertory': {
            'Meta': {'unique_together': "(('player', 'item'),)", 'object_name': 'PlayerEventRepertory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.EventRepertoryItem']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'event_repertories'", 'null': 'True', 'to': "orm['music.Player']"})
        },
        'music.rehearsal': {
            'Meta': {'object_name': 'Rehearsal'},
            'band': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Band']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'studio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['event.Location']"})
        },
        'music.repertory': {
            'Meta': {'object_name': 'Repertory'},
            'band': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'repertory'", 'unique': 'True', 'null': 'True', 'to': "orm['music.Band']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_lock': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'main_repertories'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'music.repertoryitem': {
            'Meta': {'unique_together': "(('song', 'repertory'),)", 'object_name': 'RepertoryItem'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'repertory': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['music.Repertory']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Song']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'tempo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tonality': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'music.size': {
            'Meta': {'unique_together': "(('width', 'height'),)", 'object_name': 'Size'},
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'music.song': {
            'Meta': {'unique_together': "(('name', 'album'),)", 'object_name': 'Song'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'album': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songs'", 'to': "orm['music.Album']"}),
            'audio': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'composer': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.ComposerRole']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'signature': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tempo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tonality': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'photo.photoalbum': {
            'Meta': {'object_name': 'PhotoAlbum'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cover_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_albums'", 'null': 'True', 'to': "orm['event.Event']"}),
            'flyer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['music']