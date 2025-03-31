import os
import django
import pandas as pd
from pydantic import BaseModel, ValidationError

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza 'mi_proyecto' con tu proyecto real
django.setup()

# Importar modelos de Django
from .models import Objects, ObjectCategorys, ObjectTypes

# Definir el esquema de validación con Pydantic antes de usarlo
types_mapping = {
    "Categoria": "objectCategory",
    "Tipo": "objectType"
}

class ObjectSchema(BaseModel):
    id: int
    name: str
    objectCategory: str | None # Se usará para buscar la clave foránea
    objectType: str | None # Se usará para buscar la clave foránea

# Función para importar datos del CSV
def import_data_from_csv(file_path):
    df = pd.read_csv(file_path, delimiter=';')  # Especificar separador punto y coma
    
    # Renombrar columnas si tienen nombres distintos en el CSV
    column_mapping = {
        "Categoria": "objectCategory",
        "Tipo": "objectType"
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Verificar si las columnas necesarias están presentes
    required_columns = {"id", "name", "objectCategory", "objectType"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"El CSV no contiene las columnas necesarias: {required_columns - set(df.columns)}")
    
    for index, row in df.iterrows():
        try:
            row["objectCategory"] = row["objectCategory"] if pd.notna(row["objectCategory"]) else "1"
            row["objectType"] = row["objectType"] if pd.notna(row["objectType"]) else "1"

            # Validar datos con Pydantic
            item = ObjectSchema(**row.to_dict())

            # Buscar claves foráneas
            object_category, _ = ObjectCategorys.objects.get_or_create(name=item.objectCategory)
            object_type, _ = ObjectTypes.objects.get_or_create(name=item.objectType)

            # Insertar en la base de datos
            Objects.objects.create(
                id=item.id,
                name=item.name,
                objectCategory=object_category,
                objectType=object_type
            )
            print(f"Fila {index} importada correctamente.")
        
        except ValidationError as e:
            print(f"Error en la fila {index}: {e}")
        except Exception as e:
            print(f"Error inesperado en la fila {index}: {e}")


# Llamada a la función de importación
import_data_from_csv('C:/val/valApp/valaniaObjetos.csv')
