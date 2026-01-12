from django.core.management.base import BaseCommand
from django.utils import timezone
from tata_integration.api_client import TataAPIClient
from leads.models import Lead
import requests
import json

class Command(BaseCommand):
    help = 'Auto sync Tata IVR calls, Google leads, and Meta leads'

    def handle(self, *args, **options):
        # Silent sync - no console output
        try:
            self.sync_tata_calls()
            self.sync_meta_leads()
            self.sync_google_leads()
        except:
            pass

    def sync_tata_calls(self):
        try:
            client = TataAPIClient()
            client.sync_call_records()
        except:
            pass

    def sync_meta_leads(self):
        try:
            from leads.meta_sync import sync_recent_meta_leads
            result = sync_recent_meta_leads()
            self.stdout.write(f"Meta sync: {result.get('message', 'Done')}")
        except Exception as e:
            self.stdout.write(f"Meta sync error: {str(e)}")

    def sync_google_leads(self):
        try:
            # Add Google Sheets sync here if needed
            pass
        except Exception as e:
            self.stdout.write(f"Google sync error: {str(e)}")