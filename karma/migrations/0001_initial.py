# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'karma_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('screen_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('avatar', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('banned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'karma', ['User'])

        # Adding model 'Tweet'
        db.create_table(u'karma_tweet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='karma_sends', null=True, on_delete=models.SET_NULL, to=orm['karma.User'])),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='karma_receives', null=True, on_delete=models.SET_NULL, to=orm['karma.User'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'karma', ['Tweet'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'karma_user')

        # Deleting model 'Tweet'
        db.delete_table(u'karma_tweet')


    models = {
        u'karma.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'karma_receives'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['karma.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'karma_sends'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['karma.User']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'karma.user': {
            'Meta': {'object_name': 'User'},
            'avatar': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'banned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'screen_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['karma']