# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'tickets_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'tickets', ['Category'])

        # Adding field 'Show.description'
        db.add_column(u'tickets_show', 'description',
                      self.gf('django.db.models.fields.TextField')(default='Blank'),
                      keep_default=False)

        # Adding field 'Show.long_description'
        db.add_column(u'tickets_show', 'long_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Show.poster'
        db.add_column(u'tickets_show', 'poster',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'tickets_category')

        # Deleting field 'Show.description'
        db.delete_column(u'tickets_show', 'description')

        # Deleting field 'Show.long_description'
        db.delete_column(u'tickets_show', 'long_description')

        # Deleting field 'Show.poster'
        db.delete_column(u'tickets_show', 'poster')


    models = {
        u'tickets.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tickets.occurrence': {
            'Meta': {'object_name': 'Occurrence'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'hours_til_close': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_sell': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Show']"}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        u'tickets.show': {
            'Meta': {'object_name': 'Show'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'Theatre'", 'max_length': '30'}),
            'long_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'poster': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'tickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Occurrence']"}),
            'person_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tickets']