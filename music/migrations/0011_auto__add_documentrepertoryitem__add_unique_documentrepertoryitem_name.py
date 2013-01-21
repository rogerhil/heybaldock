# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocumentRepertoryItem'
        db.create_table('music_documentrepertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.RepertoryItem'])),
            ('document', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('music', ['DocumentRepertoryItem'])

        # Adding unique constraint on 'DocumentRepertoryItem', fields ['name', 'item']
        db.create_unique('music_documentrepertoryitem', ['name', 'item_id'])

        # Adding model 'PlayerRepertoryItem'
        db.create_table('music_playerrepertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='repertory_items', null=True, to=orm['music.Player'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='players', to=orm['music.RepertoryItem'])),
            ('as_member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Artist'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('is_lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('music', ['PlayerRepertoryItem'])

        # Adding M2M table for field tag_types on 'PlayerRepertoryItem'
        db.create_table('music_playerrepertoryitem_tag_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('playerrepertoryitem', models.ForeignKey(orm['music.playerrepertoryitem'], null=False)),
            ('instrumenttagtype', models.ForeignKey(orm['music.instrumenttagtype'], null=False))
        ))
        db.create_unique('music_playerrepertoryitem_tag_types', ['playerrepertoryitem_id', 'instrumenttagtype_id'])

        # Adding unique constraint on 'PlayerRepertoryItem', fields ['player', 'item']
        db.create_unique('music_playerrepertoryitem', ['player_id', 'item_id'])

        # Adding model 'PlayerRepertoryItemRating'
        db.create_table('music_playerrepertoryitemrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='player_repertory_items_ratings', to=orm['auth.User'])),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users_ratings', to=orm['music.PlayerRepertoryItem'])),
            ('rate', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('music', ['PlayerRepertoryItemRating'])

        # Adding unique constraint on 'PlayerRepertoryItemRating', fields ['user', 'player_repertory_item']
        db.create_unique('music_playerrepertoryitemrating', ['user_id', 'player_repertory_item_id'])

        # Adding model 'MusicScoreSegment'
        db.create_table('music_musicscoresegment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
            ('score', self.gf('lib.fields.JSONField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['MusicScoreSegment'])

        # Adding unique constraint on 'MusicScoreSegment', fields ['name', 'player_repertory_item']
        db.create_unique('music_musicscoresegment', ['name', 'player_repertory_item_id'])

        # Adding model 'DocumentPlayerRepertoryItem'
        db.create_table('music_documentplayerrepertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['music.PlayerRepertoryItem'])),
            ('document', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.SmallIntegerField')(default=2)),
        ))
        db.send_create_signal('music', ['DocumentPlayerRepertoryItem'])

        # Adding unique constraint on 'DocumentPlayerRepertoryItem', fields ['name', 'player_repertory_item']
        db.create_unique('music_documentplayerrepertoryitem', ['name', 'player_repertory_item_id'])

        # Adding model 'VideoPlayerRepertoryItem'
        db.create_table('music_videoplayerrepertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recorded', self.gf('django.db.models.fields.DateField')(null=True)),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('thumbnail_small', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
        ))
        db.send_create_signal('music', ['VideoPlayerRepertoryItem'])

        # Adding model 'MusicAudioSegment'
        db.create_table('music_musicaudiosegment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
            ('audio', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['MusicAudioSegment'])

        # Adding unique constraint on 'MusicAudioSegment', fields ['name', 'player_repertory_item']
        db.create_unique('music_musicaudiosegment', ['name', 'player_repertory_item_id'])

        # Adding model 'UserRepertoryItemRating'
        db.create_table('music_userrepertoryitemrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='repertory_items_ratings', to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='users_ratings', to=orm['music.RepertoryItem'])),
            ('rate', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('music', ['UserRepertoryItemRating'])

        # Adding unique constraint on 'UserRepertoryItemRating', fields ['user', 'item']
        db.create_unique('music_userrepertoryitemrating', ['user_id', 'item_id'])

        # Adding model 'VideoRepertoryItem'
        db.create_table('music_videorepertoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recorded', self.gf('django.db.models.fields.DateField')(null=True)),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('thumbnail_small', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('player_repertory_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.PlayerRepertoryItem'])),
        ))
        db.send_create_signal('music', ['VideoRepertoryItem'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserRepertoryItemRating', fields ['user', 'item']
        db.delete_unique('music_userrepertoryitemrating', ['user_id', 'item_id'])

        # Removing unique constraint on 'MusicAudioSegment', fields ['name', 'player_repertory_item']
        db.delete_unique('music_musicaudiosegment', ['name', 'player_repertory_item_id'])

        # Removing unique constraint on 'DocumentPlayerRepertoryItem', fields ['name', 'player_repertory_item']
        db.delete_unique('music_documentplayerrepertoryitem', ['name', 'player_repertory_item_id'])

        # Removing unique constraint on 'MusicScoreSegment', fields ['name', 'player_repertory_item']
        db.delete_unique('music_musicscoresegment', ['name', 'player_repertory_item_id'])

        # Removing unique constraint on 'PlayerRepertoryItemRating', fields ['user', 'player_repertory_item']
        db.delete_unique('music_playerrepertoryitemrating', ['user_id', 'player_repertory_item_id'])

        # Removing unique constraint on 'PlayerRepertoryItem', fields ['player', 'item']
        db.delete_unique('music_playerrepertoryitem', ['player_id', 'item_id'])

        # Removing unique constraint on 'DocumentRepertoryItem', fields ['name', 'item']
        db.delete_unique('music_documentrepertoryitem', ['name', 'item_id'])

        # Deleting model 'DocumentRepertoryItem'
        db.delete_table('music_documentrepertoryitem')

        # Deleting model 'PlayerRepertoryItem'
        db.delete_table('music_playerrepertoryitem')

        # Removing M2M table for field tag_types on 'PlayerRepertoryItem'
        db.delete_table('music_playerrepertoryitem_tag_types')

        # Deleting model 'PlayerRepertoryItemRating'
        db.delete_table('music_playerrepertoryitemrating')

        # Deleting model 'MusicScoreSegment'
        db.delete_table('music_musicscoresegment')

        # Deleting model 'DocumentPlayerRepertoryItem'
        db.delete_table('music_documentplayerrepertoryitem')

        # Deleting model 'VideoPlayerRepertoryItem'
        db.delete_table('music_videoplayerrepertoryitem')

        # Deleting model 'MusicAudioSegment'
        db.delete_table('music_musicaudiosegment')

        # Deleting model 'UserRepertoryItemRating'
        db.delete_table('music_userrepertoryitemrating')

        # Deleting model 'VideoRepertoryItem'
        db.delete_table('music_videorepertoryitem')


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
        'music.documentplayerrepertoryitem': {
            'Meta': {'unique_together': "(('name', 'player_repertory_item'),)", 'object_name': 'DocumentPlayerRepertoryItem'},
            'document': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'player_repertory_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': "orm['music.PlayerRepertoryItem']"}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'})
        },
        'music.documentrepertoryitem': {
            'Meta': {'unique_together': "(('name', 'item'),)", 'object_name': 'DocumentRepertoryItem'},
            'document': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.RepertoryItem']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
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
        'music.musicaudiosegment': {
            'Meta': {'unique_together': "(('name', 'player_repertory_item'),)", 'object_name': 'MusicAudioSegment'},
            'audio': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'player_repertory_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.PlayerRepertoryItem']"})
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
        'music.musicscoresegment': {
            'Meta': {'unique_together': "(('name', 'player_repertory_item'),)", 'object_name': 'MusicScoreSegment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'player_repertory_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.PlayerRepertoryItem']"}),
            'score': ('lib.fields.JSONField', [], {})
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
        'music.playerrepertoryitem': {
            'Meta': {'unique_together': "(('player', 'item'),)", 'object_name': 'PlayerRepertoryItem'},
            'as_member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Artist']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'players'", 'to': "orm['music.RepertoryItem']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'repertory_items'", 'null': 'True', 'to': "orm['music.Player']"}),
            'tag_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.InstrumentTagType']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'music.playerrepertoryitemrating': {
            'Meta': {'unique_together': "(('user', 'player_repertory_item'),)", 'object_name': 'PlayerRepertoryItemRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player_repertory_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users_ratings'", 'to': "orm['music.PlayerRepertoryItem']"}),
            'rate': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_repertory_items_ratings'", 'to': "orm['auth.User']"})
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
        'music.userrepertoryitemrating': {
            'Meta': {'unique_together': "(('user', 'item'),)", 'object_name': 'UserRepertoryItemRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users_ratings'", 'to': "orm['music.RepertoryItem']"}),
            'rate': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'repertory_items_ratings'", 'to': "orm['auth.User']"})
        },
        'music.videoplayerrepertoryitem': {
            'Meta': {'object_name': 'VideoPlayerRepertoryItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'player_repertory_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.PlayerRepertoryItem']"}),
            'recorded': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'thumbnail_small': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'music.videorepertoryitem': {
            'Meta': {'object_name': 'VideoRepertoryItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'player_repertory_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.PlayerRepertoryItem']"}),
            'recorded': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'thumbnail_small': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
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