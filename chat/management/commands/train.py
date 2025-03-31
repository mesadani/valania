
import os
import django

# Configura Django para que cargue los settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Asegúrate de usar el nombre correcto de tu proyecto
django.setup()
# Ahora puedes importar modelos y trabajar con Django

from chat.models import Question, Answer

# Agregar preguntas y respuestas predeterminadas
def populate_data():
    # Ejemplo de preguntas y respuestas
    questions = [
        "¿Qué es Django?",
        "¿Cómo usar un modelo en Django?",
        "¿Qué es una base de datos en Django?"
    ]

    answers = [
        "Django es un framework web de alto nivel para Python.",
        "Para usar un modelo en Django, primero debes definirlo en el archivo models.py.",
        "Una base de datos en Django es donde se almacenan los datos de tu aplicación."
    ]

    for question_text, answer_text in zip(questions, answers):
        # Crear pregunta y respuesta en la base de datos
        question = Question.objects.create(text=question_text)
        Answer.objects.create(text=answer_text, question=question)

    print("Datos insertados exitosamente.")

if __name__ == '__main__':
    populate_data()

