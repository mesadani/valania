import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza 'mi_proyecto' con tu proyecto real
django.setup()

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.feature_extraction.text import TfidfVectorizer
from .models import Question, Answer

# Obtener los datos de la base de datos
questions = Question.objects.all()
answers = Answer.objects.all()

# Usar un vectorizador TF-IDF para representar las preguntas
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform([q.text for q in questions])
y = [a.text for a in answers]

# Crear un diccionario para mapear cada respuesta única a un número
answer_to_idx = {answer: idx for idx, answer in enumerate(set(y))}
y_num = [answer_to_idx[answer] for answer in y]

# Crear una red neuronal simple en PyTorch
class ChatbotModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(ChatbotModel, self).__init__()
        self.fc = nn.Linear(input_size, output_size)

    def forward(self, x):
        return self.fc(x)

input_size = X.shape[1]  # El tamaño de entrada es el número de características
output_size = len(set(y))  # Número de respuestas únicas

# Crear el modelo
model = ChatbotModel(input_size, output_size)
optimizer = optim.SGD(model.parameters(), lr=0.1)
loss_function = nn.CrossEntropyLoss()

# Entrenar el modelo
for epoch in range(100):  # Número de épocas
    optimizer.zero_grad()

    # Convierte X a un tensor de tipo flotante
    output = model(torch.Tensor(X.toarray()))  # Convierte X a un tensor denso
    loss = loss_function(output, torch.tensor(y_num, dtype=torch.long))  # Utiliza y_num

    loss.backward()
    optimizer.step()

    print(f'Epoch {epoch+1}, Loss: {loss.item()}')

# Guardar el modelo entrenado
torch.save(model.state_dict(), 'chatbot_model.pth')
