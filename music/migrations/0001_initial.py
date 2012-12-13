# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Composer'
        db.create_table('music_composer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Composer'])

        # Adding model 'Artist'
        db.create_table('music_artist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Artist'])

        # Adding model 'Album'
        db.create_table('music_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('discogsid', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('catno', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Artist'])),
            ('thumb', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['Album'])

        # Adding model 'SongStyle'
        db.create_table('music_songstyle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['SongStyle'])

        # Adding model 'Song'
        db.create_table('music_song', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Album'])),
            ('lyrics', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('style', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.SongStyle'])),
        ))
        db.send_create_signal('music', ['Song'])

        # Adding unique constraint on 'Song', fields ['name', 'album']
        db.create_unique('music_song', ['name', 'album_id'])

        # Adding M2M table for field composer on 'Song'
        db.create_table('music_song_composer', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(orm['music.song'], null=False)),
            ('composer', models.ForeignKey(orm['music.composer'], null=False))
        ))
        db.create_unique('music_song_composer', ['song_id', 'composer_id'])

        # Adding model 'Repertory'
        db.create_table('music_repertory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['event.Event'], null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Repertory'])

        # Adding unique constraint on 'Repertory', fields ['name', 'event']
        db.create_unique('music_repertory', ['name', 'event_id'])

        # Adding model 'RepertoryGroup'
        db.create_table('music_repertorygroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('repertory', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groups', to=orm['music.Repertory'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['RepertoryGroup'])

        # Adding unique constraint on 'RepertoryGroup', fields ['repertory', 'order']
        db.create_unique('music_repertorygroup', ['repertory_id', 'order'])

        # Adding model 'RepertoryGroupItem'
        db.create_table('music_repertorygroupitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Song'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songs', to=orm['music.RepertoryGroup'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['RepertoryGroupItem'])

        # Adding unique constraint on 'RepertoryGroupItem', fields ['song', 'group']
        db.create_unique('music_repertorygroupitem', ['song_id', 'group_id'])

        # Adding unique constraint on 'RepertoryGroupItem', fields ['group', 'number']
        db.create_unique('music_repertorygroupitem', ['group_id', 'number'])

        # Adding model 'Instrument'
        db.create_table('music_instrument', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('is_lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('music', ['Instrument'])

        # Adding model 'UserInstrumentSong'
        db.create_table('music_userinstrumentsong', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Instrument'])),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Song'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('music', ['UserInstrumentSong'])

        # Adding unique constraint on 'UserInstrumentSong', fields ['instrument', 'song', 'user']
        db.create_unique('music_userinstrumentsong', ['instrument_id', 'song_id', 'user_id'])

        # Adding model 'UserSongRating'
        db.create_table('music_usersongrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Song'])),
            ('rate', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('music', ['UserSongRating'])

        # Adding unique constraint on 'UserSongRating', fields ['song', 'user', 'rate']
        db.create_unique('music_usersongrating', ['song_id', 'user_id', 'rate'])

        # Adding model 'UserInstrumentSongRating'
        db.create_table('music_userinstrumentsongrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_instrument_song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.UserInstrumentSong'])),
            ('rate', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('music', ['UserInstrumentSongRating'])

        # Adding unique constraint on 'UserInstrumentSongRating', fields ['user_instrument_song', 'rate']
        db.create_unique('music_userinstrumentsongrating', ['user_instrument_song_id', 'rate'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserInstrumentSongRating', fields ['user_instrument_song', 'rate']
        db.delete_unique('music_userinstrumentsongrating', ['user_instrument_song_id', 'rate'])

        # Removing unique constraint on 'UserSongRating', fields ['song', 'user', 'rate']
        db.delete_unique('music_usersongrating', ['song_id', 'user_id', 'rate'])

        # Removing unique constraint on 'UserInstrumentSong', fields ['instrument', 'song', 'user']
        db.delete_unique('music_userinstrumentsong', ['instrument_id', 'song_id', 'user_id'])

        # Removing unique constraint on 'RepertoryGroupItem', fields ['group', 'number']
        db.delete_unique('music_repertorygroupitem', ['group_id', 'number'])

        # Removing unique constraint on 'RepertoryGroupItem', fields ['song', 'group']
        db.delete_unique('music_repertorygroupitem', ['song_id', 'group_id'])

        # Removing unique constraint on 'RepertoryGroup', fields ['repertory', 'order']
        db.delete_unique('music_repertorygroup', ['repertory_id', 'order'])

        # Removing unique constraint on 'Repertory', fields ['name', 'event']
        db.delete_unique('music_repertory', ['name', 'event_id'])

        # Removing unique constraint on 'Song', fields ['name', 'album']
        db.delete_unique('music_song', ['name', 'album_id'])

        # Deleting model 'Composer'
        db.delete_table('music_composer')

        # Deleting model 'Artist'
        db.delete_table('music_artist')

        # Deleting model 'Album'
        db.delete_table('music_album')

        # Deleting model 'SongStyle'
        db.delete_table('music_songstyle')

        # Deleting model 'Song'
        db.delete_table('music_song')

        # Removing M2M table for field composer on 'Song'
        db.delete_table('music_song_composer')

        # Deleting model 'Repertory'
        db.delete_table('music_repertory')

        # Deleting model 'RepertoryGroup'
        db.delete_table('music_repertorygroup')

        # Deleting model 'RepertoryGroupItem'
        db.delete_table('music_repertorygroupitem')

        # Deleting model 'Instrument'
        db.delete_table('music_instrument')

        # Deleting model 'UserInstrumentSong'
        db.delete_table('music_userinstrumentsong')

        # Deleting model 'UserSongRating'
        db.delete_table('music_usersongrating')

        # Deleting model 'UserInstrumentSongRating'
        db.delete_table('music_userinstrumentsongrating')


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
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'phone1': ('django.db.models.fields.IntegerField', [], {}),
            'phone2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'phone3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'music.album': {
            'Meta': {'object_name': 'Album'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Artist']"}),
            'catno': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'discogsid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'thumb': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'music.artist': {
            'Meta': {'object_name': 'Artist'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.composer': {
            'Meta': {'object_name': 'Composer'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.repertory': {
            'Meta': {'unique_together': "(('name', 'event'),)", 'object_name': 'Repertory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['event.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'music.repertorygroup': {
            'Meta': {'unique_together': "(('repertory', 'order'),)", 'object_name': 'RepertoryGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'repertory': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['music.Repertory']"})
        },
        'music.repertorygroupitem': {
            'Meta': {'unique_together': "(('song', 'group'), ('group', 'number'))", 'object_name': 'RepertoryGroupItem'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songs'", 'to': "orm['music.RepertoryGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Song']"})
        },
        'music.song': {
            'Meta': {'unique_together': "(('name', 'album'),)", 'object_name': 'Song'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Album']"}),
            'composer': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.Composer']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.SongStyle']"})
        },
        'music.songstyle': {
            'Meta': {'object_name': 'SongStyle'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'music.userinstrumentsong': {
            'Meta': {'unique_together': "(('instrument', 'song', 'user'),)", 'object_name': 'UserInstrumentSong'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Instrument']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Song']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'music.userinstrumentsongrating': {
            'Meta': {'unique_together': "(('user_instrument_song', 'rate'),)", 'object_name': 'UserInstrumentSongRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user_instrument_song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.UserInstrumentSong']"})
        },
        'music.usersongrating': {
            'Meta': {'unique_together': "(('song', 'user', 'rate'),)", 'object_name': 'UserSongRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.SmallIntegerField', [], {}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Song']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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