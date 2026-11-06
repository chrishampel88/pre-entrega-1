"""Cliente simple de OpenAI y Anthropic: modo normal y streaming."""

import asyncio
import os
import sys

from dotenv import load_dotenv
from pydantic import ValidationError
from schemas import ChatMessage, ModelConfig, ModelResponse

load_dotenv()


class AsyncLLMManager:
    def __init__(self, proveedor: str):
        # Elegimos qué proveedor usar sin cambiar el resto del programa.
        self.proveedor = proveedor.lower()

        if self.proveedor == "openai":
            from openai import AsyncOpenAI

            clave = os.getenv("OPENAI_API_KEY")
            if not clave:
                raise ValueError("Falta OPENAI_API_KEY en el archivo .env")
            self.cliente = AsyncOpenAI(api_key=clave)
            self.modelo = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        elif self.proveedor == "anthropic":
            from anthropic import AsyncAnthropic

            clave = os.getenv("ANTHROPIC_API_KEY")
            if not clave:
                raise ValueError("Falta ANTHROPIC_API_KEY en el archivo .env")
            self.cliente = AsyncAnthropic(api_key=clave)
            self.modelo = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

        else:
            raise ValueError("Proveedor no válido. Usá openai o anthropic")

    def _datos_anthropic(self, mensajes):
        # Anthropic recibe el mensaje 'system' por separado.
        sistema = "\n".join(m.content for m in mensajes if m.role == "system")
        conversacion = [
            m.model_dump() for m in mensajes if m.role != "system"
        ]
        datos = {"messages": conversacion}
        if sistema:
            datos["system"] = sistema
        return datos

    def _error(self, error):
        # Traducimos las excepciones de ambos proveedores a textos simples.
        import openai
        import anthropic

        if isinstance(error, (openai.RateLimitError, anthropic.RateLimitError)):
            return "Límite de solicitudes o cuota alcanzado. Revisá tus créditos."
        if isinstance(error, (openai.APIConnectionError, anthropic.APIConnectionError)):
            return "Error de conexión o tiempo de espera con la API."
        return "La API devolvió un error. Revisá la clave, el modelo y tu cuenta."

    async def generar(self, mensajes: list[ChatMessage], config: ModelConfig) -> ModelResponse:
        """Modo normal: espera hasta recibir la respuesta completa."""
        import openai
        import anthropic

        try:
            if self.proveedor == "openai":
                respuesta = await self.cliente.chat.completions.create(
                    model=self.modelo,
                    messages=[m.model_dump() for m in mensajes],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
                texto = respuesta.choices[0].message.content or ""
            else:
                respuesta = await self.cliente.messages.create(
                    model=self.modelo,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    **self._datos_anthropic(mensajes),
                )
                texto = "".join(b.text for b in respuesta.content if b.type == "text")
            return ModelResponse(provider=self.proveedor, content=texto)
        except (openai.APIError, anthropic.APIError) as error:
            return ModelResponse(provider=self.proveedor, content="", error=self._error(error))

    async def generar_stream(self, mensajes: list[ChatMessage], config: ModelConfig):
        """Streaming: yield entrega fragmentos conforme llegan."""
        import openai
        import anthropic

        try:
            if self.proveedor == "openai":
                stream = await self.cliente.chat.completions.create(
                    model=self.modelo,
                    messages=[m.model_dump() for m in mensajes],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    stream=True,
                )
                async for parte in stream:
                    texto = parte.choices[0].delta.content
                    if texto:
                        yield texto
            else:
                async with self.cliente.messages.stream(
                    model=self.modelo,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    **self._datos_anthropic(mensajes),
                ) as stream:
                    async for texto in stream.text_stream:
                        yield texto
        except (openai.APIError, anthropic.APIError) as error:
            yield f"\n[ERROR] {self._error(error)}"

    async def cerrar(self):
        await self.cliente.close()


async def main():
    # Demo: permite verificar la estructura aunque no tengas créditos.
    proveedor = sys.argv[1].lower() if len(sys.argv) > 1 else "demo"
    mensajes = [ChatMessage(role="user", content="¿Qué es la entropía? Respondé breve.")]
    config = ModelConfig(temperature=0.7, max_tokens=200)

    if proveedor == "demo":
        print("MODO NORMAL (simulado):")
        print("La entropía mide dispersión o incertidumbre.")
        print("\nMODO STREAMING (simulado):")
        for fragmento in ["La entropía ", "mide dispersión ", "o incertidumbre."]:
            print(fragmento, end="", flush=True)
            await asyncio.sleep(0.2)
        print()
        return

    cliente = None
    try:
        cliente = AsyncLLMManager(proveedor)
        print("MODO NORMAL:")
        respuesta = await cliente.generar(mensajes, config)
        print(f"[ERROR] {respuesta.error}" if respuesta.error else respuesta.content)

        print("\nMODO STREAMING:")
        async for fragmento in cliente.generar_stream(mensajes, config):
            print(fragmento, end="", flush=True)
        print()
    except (ValueError, ValidationError) as error:
        print(f"[ERROR] {error}")
    finally:
        if cliente is not None:
            await cliente.cerrar()


if __name__ == "__main__":
    asyncio.run(main())
