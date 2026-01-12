from django.core.management.base import BaseCommand
import subprocess
import sys

class Command(BaseCommand):
    help = 'Start Celery worker and beat scheduler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--worker-only',
            action='store_true',
            help='Start only the worker, not the beat scheduler',
        )

    def handle(self, *args, **options):
        if options['worker_only']:
            self.stdout.write('Starting Celery worker...')
            subprocess.run([
                sys.executable, '-m', 'celery', 
                '-A', 'crm', 'worker', 
                '--loglevel=info'
            ])
        else:
            self.stdout.write('Starting Celery worker and beat scheduler...')
            # Start worker in background
            worker_process = subprocess.Popen([
                sys.executable, '-m', 'celery', 
                '-A', 'crm', 'worker', 
                '--loglevel=info'
            ])
            
            # Start beat scheduler
            beat_process = subprocess.Popen([
                sys.executable, '-m', 'celery', 
                '-A', 'crm', 'beat', 
                '--loglevel=info'
            ])
            
            try:
                worker_process.wait()
                beat_process.wait()
            except KeyboardInterrupt:
                worker_process.terminate()
                beat_process.terminate()
                self.stdout.write('Celery processes terminated.')