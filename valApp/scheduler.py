# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from valApp.funciones import functions

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(functions.actualizarPrecios, 'interval', minutes=10)
    scheduler.start()
