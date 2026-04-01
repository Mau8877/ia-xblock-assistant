import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Cargar las variables secretas del archivo .env
load_dotenv()

# 2. Leer la llave de forma segura
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("¡Cuidado Mauro! No se encontró la OPENROUTER_API_KEY en el archivo .env")

# 3. Inicializar el cliente
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

print("Enviando mensaje a la IA (de forma segura)...")

# 4. Llamada al modelo (Usando uno gratuito actualizado)
completion = client.chat.completions.create(
  model="qwen/qwen3.6-plus-preview:free",
  messages=[
    {"role": "system", "content": "Eres un profesor universitario de la UAGRM especializado en tecnología."},
    {"role": "user", "content": "Explícame en un párrafo corto qué es Open edX."}
  ]
)

print("\n🤖 Respuesta de la IA:")
print(completion.choices[0].message.content)