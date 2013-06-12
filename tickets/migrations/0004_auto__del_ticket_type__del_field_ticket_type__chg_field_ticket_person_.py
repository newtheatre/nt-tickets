# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Ticket_Type'
        db.delete_table(u'tickets_ticket_type')

        # Deleting field 'Ticket.type'
        db.delete_column(u'tickets_ticket', 'type_id')


        # Changing field 'Ticket.person_name'
        db.alter_column(u'tickets_ticket', 'person_name', self.gf('django.db.models.fields.CharField')(max_length=80))

        # Changing field 'Ticket.email_address'
        db.alter_column(u'tickets_ticket', 'email_address', self.gf('django.db.models.fields.EmailField')(max_length=80))
        # Removing M2M table for field tickets_available on 'Occurrence'
        db.delete_table(db.shorten_name(u'tickets_occurrence_tickets_available'))


    def backwards(self, orm):
        # Adding model 'Ticket_Type'
        db.create_table(u'tickets_ticket_type', (
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('tickets', ['Ticket_Type'])


        # User chose to not deal with backwards NULL issues for 'Ticket.type'
        raise RuntimeError("Cannot reverse this migration. 'Ticket.type' and its values cannot be restored.")

        # Changing field 'Ticket.person_name'
        db.alter_column(u'tickets_ticket', 'person_name', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'Ticket.email_address'
        db.alter_column(u'tickets_ticket', 'email_address', self.gf('django.db.models.fields.EmailField')(max_length=40))
        # Adding M2M table for field tickets_available on 'Occurrence'
        m2m_table_name = db.shorten_name(u'tickets_occurrence_tickets_available')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('occurrence', models.ForeignKey(orm['tickets.occurrence'], null=False)),
            ('ticket_type', models.ForeignKey(orm['tickets.ticket_type'], null=False))
        ))
        db.create_unique(m2m_table_name, ['occurrence_id', 'ticket_type_id'])


    models = {
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'Theatre'", 'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'tickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Occurrence']"}),
            'person_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tickets']