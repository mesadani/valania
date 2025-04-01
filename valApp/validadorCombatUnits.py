import os
import sys
import django
import pandas as pd
from pydantic import BaseModel, ValidationError, constr, conint, confloat

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valProject.settings')  # Reemplaza con tu proyecto
django.setup()

# Importar modelos de Django
from valApp.models import CombatUnits, Races, Rarities, RolesCombatUnits  # Ajusta el import según tu estructura

# Definir el esquema de validación con Pydantic
class CombatUnitSchema(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    rarity: constr(strip_whitespace=True, min_length=1)
    type: constr(strip_whitespace=True, min_length=1)
    tp: conint(ge=0)  # TP debe ser un entero positivo
    price: confloat(ge=0)  # Precio debe ser un número positivo
    supply: conint(ge=0)  # Supply debe ser un número positivo

# Función para importar datos desde un archivo Excel
def import_data_from_excel(file_path):
    # Leer el archivo Excel con todas sus hojas
    xls = pd.ExcelFile(file_path)

    for sheet_name in xls.sheet_names:  # Iterar sobre cada hoja
        print(f"📄 Procesando hoja: {sheet_name}")

        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Renombrar columnas si tienen nombres distintos en el Excel
        column_mapping = {
            "Name": "name",
            "Rarity": "rarity",
            "Type": "type",
            "TP": "tp",
            "Price": "price",
            "Supply": "supply"
        }
        df.rename(columns=column_mapping, inplace=True)

        # Verificar si las columnas necesarias están presentes
        required_columns = {"name", "rarity", "type", "tp", "price", "supply"}
        if not required_columns.issubset(df.columns):
            print(f"⚠️ La hoja '{sheet_name}' no contiene las columnas necesarias: {required_columns - set(df.columns)}")
            continue

        # Iterar sobre cada fila del DataFrame
        for index, row in df.iterrows():
            try:
                # Validar datos con Pydantic
                item = CombatUnitSchema(**row.to_dict())

                # Insertar en la base de datos
                race, _ = Races.objects.get_or_create(name=sheet_name)
                rarity, _ = Rarities.objects.get_or_create(name=item.rarity)
                role, _ = RolesCombatUnits.objects.get_or_create(name=item.type)

                CombatUnits.objects.create(
                    race=race,
                    name=item.name,
                    rarity=rarity,
                    role=role,
                    troopPoints=item.tp,
                    price=item.price,
                    supply=item.supply
                )
                print(f"✅ Fila {index} de la hoja '{sheet_name}' importada correctamente.")

            except ValidationError as e:
                print(f"❌ Error en la fila {index} de la hoja '{sheet_name}': {e}")
            except Exception as e:
                print(f"⚠️ Error inesperado en la fila {index} de la hoja '{sheet_name}': {e}")

# Ejecutar la importación
import_data_from_excel('C:/MAMP/htdocs/piton/valApp/combatUnit.xlsx')  # Cambia por la ruta real del archivo
