from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.group_name = f'user_{self.scope["user"].id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Manejar mensajes recibidos del cliente si es necesario
        data = json.loads(text_data)
        message = data.get('message', '')

        # Aquí puedes procesar el mensaje recibido y enviar una respuesta si es necesario
        await self.send(text_data=json.dumps({
            'message': f"Echo: {message}"
        }))

    async def send_notification(self, event):
        # Enviar notificación al cliente
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
