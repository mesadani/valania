from transformers import pipeline
import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza 'mi_proyecto' con tu proyecto real
django.setup()



# Cargar un pipeline de conversación
chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

# Probar el modelo con una entrada de ejemplo
response = chatbot("Hola, ¿cómo estás?")
print(response)
