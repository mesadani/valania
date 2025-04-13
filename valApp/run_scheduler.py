
import os
import sys
import django
import logging



# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurar el entorno de Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza con tu proyecto
django.setup()
from valApp.models import *  # Cambiado a importación absoluta
from apscheduler.schedulers.background import BackgroundScheduler
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
logging.info(f"Running in virtual environment: {os.environ.get('VIRTUAL_ENV')}")

def detectPricesNoti():
    channel_layer = get_channel_layer()
    
    # Filtrar solo las notificaciones de usuario que están disponibles
    user_notifications = UserNotification.objects.filter(available=True)
    logging.info(f"Found {user_notifications.count()} user notifications available.")

    for user_notification in user_notifications:
        obj_price = ObjectsPrices.objects.filter(
            object=user_notification.object,
            price__lte=user_notification.price
        ).first()

        if obj_price:
            message = f"El objeto {obj_price.object.name} está disponible por {obj_price.price}."
            Notification.objects.create(user=user_notification.user, message=message)
            logging.info(f"Notificación enviada a {user_notification.user.username}: {message}")

            # Enviar notificación a través del canal
            async_to_sync(channel_layer.group_send)(
                f'user_{user_notification.user.id}',
                {
                    'type': 'send_notification',
                    'message': message
                }
            )

            # Marcar la notificación como no disponible
            user_notification.available = False
            user_notification.save()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(detectPricesNoti, 'interval', minutes=1)
    scheduler.start()
    logging.info("Scheduler started.")

if __name__ == "__main__":
    start_scheduler()
    try:
        # Mantener el script en ejecución
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
