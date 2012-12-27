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
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('discogs_resource_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('metadata', self.gf('lib.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Composer'])

        # Adding model 'ComposerRole'
        db.create_table('music_composerrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('composer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Composer'])),
        ))
        db.send_create_signal('music', ['ComposerRole'])

        # Adding unique constraint on 'ComposerRole', fields ['role', 'composer']
        db.create_unique('music_composerrole', ['role', 'composer_id'])

        # Adding model 'Artist'
        db.create_table('music_artist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('metadata', self.gf('lib.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Artist'])

        # Adding model 'AlbumStyle'
        db.create_table('music_albumstyle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('music', ['AlbumStyle'])

        # Adding model 'AlbumGenre'
        db.create_table('music_albumgenre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('music', ['AlbumGenre'])

        # Adding model 'Album'
        db.create_table('music_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Artist'])),
            ('thumb', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('metadata', self.gf('lib.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Album'])

        # Adding unique constraint on 'Album', fields ['name', 'artist']
        db.create_unique('music_album', ['name', 'artist_id'])

        # Adding M2M table for field style on 'Album'
        db.create_table('music_album_style', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm['music.album'], null=False)),
            ('albumstyle', models.ForeignKey(orm['music.albumstyle'], null=False))
        ))
        db.create_unique('music_album_style', ['album_id', 'albumstyle_id'])

        # Adding M2M table for field genre on 'Album'
        db.create_table('music_album_genre', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm['music.album'], null=False)),
            ('albumgenre', models.ForeignKey(orm['music.albumgenre'], null=False))
        ))
        db.create_unique('music_album_genre', ['album_id', 'albumgenre_id'])

        # Adding model 'AlbumCoverType'
        db.create_table('music_albumcovertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('music', ['AlbumCoverType'])

        # Adding model 'Size'
        db.create_table('music_size', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['Size'])

        # Adding unique constraint on 'Size', fields ['width', 'height']
        db.create_unique('music_size', ['width', 'height'])

        # Adding model 'AlbumCover'
        db.create_table('music_albumcover', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Album'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.AlbumCoverType'], null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Size'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('music', ['AlbumCover'])

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
            ('tempo', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['Song'])

        # Adding unique constraint on 'Song', fields ['name', 'album']
        db.create_unique('music_song', ['name', 'album_id'])

        # Adding M2M table for field composer on 'Song'
        db.create_table('music_song_composer', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(orm['music.song'], null=False)),
            ('composerrole', models.ForeignKey(orm['music.composerrole'], null=False))
        ))
        db.create_unique('music_song_composer', ['song_id', 'composerrole_id'])

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

        # Removing unique constraint on 'Size', fields ['width', 'height']
        db.delete_unique('music_size', ['width', 'height'])

        # Removing unique constraint on 'Album', fields ['name', 'artist']
        db.delete_unique('music_album', ['name', 'artist_id'])

        # Removing unique constraint on 'ComposerRole', fields ['role', 'composer']
        db.delete_unique('music_composerrole', ['role', 'composer_id'])

        # Deleting model 'Composer'
        db.delete_table('music_composer')

        # Deleting model 'ComposerRole'
        db.delete_table('music_composerrole')

        # Deleting model 'Artist'
        db.delete_table('music_artist')

        # Deleting model 'AlbumStyle'
        db.delete_table('music_albumstyle')

        # Deleting model 'AlbumGenre'
        db.delete_table('music_albumgenre')

        # Deleting model 'Album'
        db.delete_table('music_album')

        # Removing M2M table for field style on 'Album'
        db.delete_table('music_album_style')

        # Removing M2M table for field genre on 'Album'
        db.delete_table('music_album_genre')

        # Deleting model 'AlbumCoverType'
        db.delete_table('music_albumcovertype')

        # Deleting model 'Size'
        db.delete_table('music_size')

        # Deleting model 'AlbumCover'
        db.delete_table('music_albumcover')

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
            'Meta': {'unique_together': "(('name', 'artist'),)", 'object_name': 'Album'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Artist']"}),
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
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.AlbumCoverType']", 'null': 'True', 'blank': 'True'})
        },
        'music.albumcovertype': {
            'Meta': {'object_name': 'AlbumCoverType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('lib.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
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
        'music.size': {
            'Meta': {'unique_together': "(('width', 'height'),)", 'object_name': 'Size'},
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'music.song': {
            'Meta': {'unique_together': "(('name', 'album'),)", 'object_name': 'Song'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Album']"}),
            'composer': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['music.ComposerRole']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'tempo': ('django.db.models.fields.IntegerField', [], {})
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