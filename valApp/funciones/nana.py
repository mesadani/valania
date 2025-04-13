import logging
from valApp.models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
def detectPricesNoti():
    channel_layer = get_channel_layer()
    object_prices = ObjectsPrices.objects.all()
    logging.info(f"Found {len(object_prices)} object prices.")

    notified_objects = set()

    for obj_price in object_prices:
        if obj_price.object.id in notified_objects:
            continue

        user_notifications = UserNotification.objects.filter(
            object=obj_price.object,
            price__lte=obj_price.price
        )

        logging.info(f"Object: {obj_price.object.name}, Price: {obj_price.price}, Notifications: {user_notifications.count()}")

        for user_notification in user_notifications:
            message = f"El objeto {obj_price.object.name} está disponible por {obj_price.price}."
            Notification.objects.create(user=user_notification.user, message=message)
            logging.info(f"Notificación enviada a {user_notification.user.username}: {message}")

            # Enviar notificación a través del canal
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user_notification.user.id}',
                {
                    'type': 'send_notification',
                    'message': message
                }
            )

        notified_objects.add(obj_price.object.id)

            