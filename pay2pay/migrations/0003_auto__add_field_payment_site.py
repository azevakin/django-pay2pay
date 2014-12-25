# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Payment.site'
        db.add_column('pay2pay_payment', 'site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Payment.site'
        db.delete_column('pay2pay_payment', 'site_id')


    models = {
        'pay2pay.payment': {
            'Meta': {'ordering': "('created',)", 'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '12', 'decimal_places': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'RUB'", 'max_length': '8'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'error_msg': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5026'}),
            'order_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'paymode': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'process'", 'max_length': '16'}),
            'test_mode': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'trans_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "'1.3'", 'max_length': '8'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pay2pay']
