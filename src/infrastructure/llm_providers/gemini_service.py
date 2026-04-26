"""Google Gemini provider implementation.

Implementa el proveedor de IA usando Google Gemini 1.5 Flash.
Construye prompts contextualizados con productos disponibles e historial del chat.
Comunica con la API de Google para generar respuestas de asesor de ventas.
Tiene un fallback determinístico si la API no está disponible.
Estructura el prompt en español para vender zapatos de forma profesional.
"""

from __future__ import annotations

from src.application.chat_service import ILLMProvider
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.domain.entities import ChatContext, Product

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None


class GeminiService(ILLMProvider):
    """Gemini integration with conversational sales prompt."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        """Configure Gemini provider.

        Args:
            api_key: Gemini API key.
            model_name: Gemini model name.
        """
        self._api_key = api_key or GEMINI_API_KEY
        self._model_name = model_name or GEMINI_MODEL

    def generate_response(
        self,
        current_message: str,
        available_products: list[Product],
        context: ChatContext,
    ) -> str:
        """Generate a sales-assistant response.

        Args:
            current_message: Latest user message.
            available_products: Available products.
            context: Recent chat context.

        Returns:
            str: Assistant response text.
        """
        prompt = self._build_prompt(current_message, available_products, context)

        if not self._api_key or genai is None:
            return self._fallback_response(available_products)

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(self._model_name)
        result = model.generate_content(prompt)
        text = getattr(result, "text", None)
        if text and text.strip():
            return text.strip()
        return self._fallback_response(available_products)

    def _build_prompt(self, current_message: str, products: list[Product], context: ChatContext) -> str:
        """Build context-rich sales prompt for Gemini.

        Args:
            current_message: Current user message.
            products: Available products list.
            context: Recent message context.

        Returns:
            str: Prompt string.
        """
        product_lines = [
            f"- {p.name} | Marca: {p.brand} | Categoria: {p.category} | Talla: {p.size} | Color: {p.color} | Precio: ${p.price:.2f} | Stock: {p.stock}"
            for p in products
        ]
        history_lines = [f"{m.role}: {m.content}" for m in context.messages]

        products_block = "\n".join(product_lines) if product_lines else "No hay productos disponibles"
        history_block = "\n".join(history_lines) if history_lines else "Sin historial previo"

        return (
            "Eres un asesor experto de ventas en una tienda de zapatos. "
            "Responde en espanol, con tono amable y profesional. "
            "Recomienda maximo 3 productos relevantes usando precio, talla y stock real. "
            "Si no hay coincidencia exacta, sugiere alternativas cercanas.\n\n"
            f"Productos disponibles:\n{products_block}\n\n"
            f"Historial reciente (ultimos 6 mensajes):\n{history_block}\n\n"
            f"Mensaje del cliente: {current_message}\n\n"
            "Respuesta esperada: asesoramiento de compra con recomendaciones concretas."
        )

    @staticmethod
    def _fallback_response(products: list[Product]) -> str:
        """Return deterministic response when Gemini is unavailable.

        Args:
            products: Available products.

        Returns:
            str: Fallback response.
        """
        top = products[:3]
        if not top:
            return "No tengo productos disponibles en este momento."

        suggestions = "\n".join(
            f"- {p.name} ({p.brand}) | Talla {p.size} | ${p.price:.2f} | Stock {p.stock}" for p in top
        )
        return (
            "Te puedo recomendar estas opciones de zapatos disponibles ahora:\n"
            f"{suggestions}\n"
            "Si me dices marca, talla o presupuesto, te doy una recomendacion mas precisa."
        )
