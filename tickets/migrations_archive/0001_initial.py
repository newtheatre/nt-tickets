# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ticket_Type'
        db.create_table('tickets_ticket_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('tickets', ['Ticket_Type'])

        # Adding model 'Show'
        db.create_table('tickets_show', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('location', self.gf('django.db.models.fields.CharField')(default='Theatre', max_length=30)),
        ))
        db.send_create_signal('tickets', ['Show'])

        # Adding model 'Occurrence'
        db.create_table('tickets_occurrence', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('show', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tickets.Show'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('maximum_sell', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('hours_til_close', self.gf('django.db.models.fields.IntegerField')(default=3)),
        ))
        db.send_create_signal('tickets', ['Occurrence'])

        # Adding model 'Ticket'
        db.create_table('tickets_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('occurrence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tickets.Occurrence'])),
            ('stamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('person_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=40)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tickets.Ticket_Type'])),
        ))
        db.send_create_signal('tickets', ['Ticket'])


    def backwards(self, orm):
        # Deleting model 'Ticket_Type'
        db.delete_table('tickets_ticket_type')

        # Deleting model 'Show'
        db.delete_table('tickets_show')

        # Deleting model 'Occurrence'
        db.delete_table('tickets_occurrence')

        # Deleting model 'Ticket'
        db.delete_table('tickets_ticket')


    models = {
        'tickets.occurrence': {
            'Meta': {'object_name': 'Occurrence'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'hours_til_close': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_sell': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tickets.Show']"}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'tickets.show': {
            'Meta': {'object_name': 'Show'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'Theatre'", 'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'tickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tickets.Occurrence']"}),
            'person_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tickets.Ticket_Type']"})
        },
        'tickets.ticket_type': {
            'Meta': {'object_name': 'Ticket_Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'})
        }
    }

    complete_apps = ['tickets']