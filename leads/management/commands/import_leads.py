from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from leads.models import Lead
import sqlite3
import os

class Command(BaseCommand):
    help = 'Import leads from existing SQLite database'

    def handle(self, *args, **options):
        db_path = 'leads.db'
        if not os.path.exists(db_path):
            self.stdout.write('No leads.db found. Run sync first.')
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.execute('SELECT * FROM leads')
        leads_data = cursor.fetchall()
        conn.close()

        imported = 0
        for row in leads_data:
            lead, created = Lead.objects.get_or_create(
                lead_id=row[1],
                defaults={
                    'created_time': parse_datetime(row[2]),
                    'email': row[3] or '',
                    'full_name': row[4] or '',
                    'phone_number': row[5] or '',
                    'form_name': row[6] or 'Unknown',
                }
            )
            if created:
                imported += 1

        self.stdout.write(f'Imported {imported} leads to Django CRM')