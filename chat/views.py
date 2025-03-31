import torch
import numpy as np
import re
import random
from django.shortcuts import render
from django.http import JsonResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from valApp.models import Races, Heroes
from .train_model import ChatbotModel
from .models import Question, Answer

# Cargar el modelo de IA y configurar el vectorizador
questions = Question.objects.all()
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform([q.text for q in questions])

input_size = X.shape[1]
output_size = len(set([a.text for a in Answer.objects.all()]))

model = ChatbotModel(input_size, output_size)
model.load_state_dict(torch.load('chatbot_model.pth'))
model.eval()

def search_in_models(name):
    """
    Función que busca el 'name' en los modelos 'Heroes' y 'Races' y otros modelos que quieras.
    """
    # Buscar en la tabla de Heroes (ahora usamos filter en vez de get)
    heroes = Heroes.objects.filter(name__iexact=name)  # Buscar héroe por nombre

    if heroes.exists():
        # Si hay más de un héroe con el mismo nombre, elegimos el primero o puedes agregar más lógica aquí
        if heroes.count() > 1:
            response = f"¡Vaya! Encontré varios héroes con el nombre '{name}'. Aquí tienes algunos de ellos: "
            heroes_info = "\n".join([f"- {heroe.name}: {heroe.description}" for heroe in heroes])
            response += "\n" + heroes_info
        else:
            # Si solo hay un héroe, devolver la información del primer héroe encontrado
            heroe = heroes.first()
            response = random.choice([
                f"¡Ah, {heroe.name}! Este héroe es impresionante. Su descripción es: {heroe.description}. ¿Te gustaría saber más sobre sus habilidades?",
                f"¡Conozco a {heroe.name}! Es uno de los héroes más poderosos. Aquí está su descripción: {heroe.description}. ¿Te gustaría conocer más acerca de su historia?"
            ])
        return 'hero', response

    # Buscar en la tabla de Races
    try:
        raza = Races.objects.get(name__iexact=name)  # Buscar raza por nombre
        heroes = Heroes.objects.filter(race=raza)  # Buscar héroes relacionados
        heroes_info = "\n".join([f" - {heroe.name}: {heroe.description}" for heroe in heroes])
        response = random.choice([
            f"¡Oh, la raza {raza.name} es fascinante! Esta es su descripción: {raza.description}. Además, tiene los siguientes héroes: {heroes_info}. ¿Te gustaría saber más sobre alguno de ellos?",
            f"La raza {raza.name} tiene una historia increíble. Su descripción es: {raza.description}. Además, sus héroes más conocidos son: {heroes_info}. ¿Cuál te gustaría conocer más?"
        ])
        return 'race', response

    except Races.DoesNotExist:
        pass

    return None, None


def chat(request):
    user_input = request.GET.get('user_input')
    if user_input:
        # Vectorizar la entrada del usuario
        user_input_vec = vectorizer.transform([user_input]).toarray()
        user_input_tensor = torch.Tensor(user_input_vec)

        # Obtener la predicción del modelo
        output = model(user_input_tensor)
        predicted_answer_index = np.argmax(output.detach().numpy())

        # Verifica si la confianza en la predicción es lo suficientemente alta
        confidence = np.max(output.detach().numpy())
        confidence_threshold = 0.6

        # Primero, chequeamos si la pregunta tiene que ver con razas o héroes
        raza_match = re.search(r'raza (\w+)', user_input.lower())
        heroe_match = re.search(r'(\w+)', user_input.lower())  # Buscamos cualquier palabra que podría ser un héroe o raza

        # Buscar en los modelos
        if raza_match:
            race_name = raza_match.group(1)
            result_type, response = search_in_models(race_name)
            if result_type:
                return JsonResponse({'response': response})

        if heroe_match:
            heroe_name = heroe_match.group(1)
            result_type, response = search_in_models(heroe_name)
            if result_type:
                return JsonResponse({'response': response})

        # Si la confianza en la predicción es suficientemente alta, devolver la respuesta estándar del modelo
        if confidence >= confidence_threshold:
            predicted_answer_index = int(predicted_answer_index)  # Convertir a entero
            if predicted_answer_index < len(Answer.objects.all()):
                answer = Answer.objects.all()[predicted_answer_index]
                return JsonResponse({'response': random.choice([
                    answer.text,
                    f"Ah, eso me recuerda algo sobre: {answer.text}. ¿Quieres saber más?",
                    f"{answer.text}... ¿Te gustaría que profundice en ese tema?"
                ])})

        # Si la predicción es baja y no se encontró ninguna raza o héroe
        return JsonResponse({'response': random.choice([
            "Lo siento, no estoy seguro de cómo responder a eso. ¿Podrías reformular la pregunta?",
            "Hmm, no entiendo bien. ¿Podrías decirlo de otra manera?",
            "Vaya, eso es complicado... No estoy seguro de cómo responder. ¿Puedes intentar preguntar de otra forma?"
        ])})

    return render(request, 'chat/chat.html')
