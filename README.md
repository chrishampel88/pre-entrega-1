# Pre-entrega 1: Cliente LLM asíncrono

Proyecto del curso de AI Engineering. Permite elegir OpenAI o Anthropic y generar respuestas en modo normal o streaming.

## Requisitos

- Python 3.12 (la consigna pide esa versión).
- Una clave de API y créditos disponibles para el proveedor elegido, solo para pruebas reales.

## Instalación (Windows, Git Bash)

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

## Variables de entorno

Copiar `.env.example` con el nombre `.env` y completar:

- `OPENAI_API_KEY`: necesaria para probar OpenAI.
- `ANTHROPIC_API_KEY`: necesaria para probar Anthropic.
- `OPENAI_MODEL` y `ANTHROPIC_MODEL`: opcionales; nombres de los modelos que usarán las APIs.

`.env` no se sube a GitHub porque contiene claves privadas.

## Ejecución

Prueba sin API ni créditos:

```bash
python main.py demo
```

Pruebas reales (pueden tener costos):

```bash
python main.py openai
python main.py anthropic
```

En ambos casos el script muestra primero el **modo normal**, que espera la respuesta completa, y después el **modo streaming**, que imprime fragmentos usando `async for` y `yield`.

## Estructura

- `main.py`: clase `AsyncLLMManager` y pruebas normal/streaming.
- `schemas.py`: modelos Pydantic `ChatMessage`, `ModelConfig` y `ModelResponse`.
- `.env.example`: variables necesarias.
- `requirements.txt`: librerías Python.
- `.gitignore`: evita subir secretos y el entorno virtual.

## Manejo de errores

El cliente captura errores reportados por los SDKs, como los de conexión o límite de solicitudes. En modo normal devuelve `ModelResponse.error`; en streaming muestra un fragmento `[ERROR]`. El modo demo no verifica el funcionamiento de las APIs reales.

## Nota

Los SDKs y modelos deben estar habilitados en la cuenta correspondiente. Si OpenAI indica que no quedan créditos, la prueba real no podrá devolver texto hasta resolverlo.


El modo demo permite observar una simulación de respuesta normal y streaming sin utilizar créditos de API. No prueba la conexión real ni el funcionamiento de los clientes OpenAI y Anthropic.