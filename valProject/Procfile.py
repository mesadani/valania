web: daphne -u /tmp/daphne.sock valApp.asgi:application
worker: python valApp/run_scheduler.py
