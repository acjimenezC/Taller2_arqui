"""Servicio de aplicación que orquesta el chat con IA."""
# Importa anotaciones de tipos de versiones futuras de Python
from __future__ import annotations

# Importa ABC (Abstract Base Class) para crear interfaces y abstractmethod para métodos abstractos
from abc import ABC, abstractmethod
# Importa funciones para manejar fechas/horas y zonas horarias
from datetime import datetime, timezone

# Importa las entidades de dominio: ChatContext (contexto del chat) y ChatMessage (mensaje del chat)
from src.domain.entities import ChatContext, ChatMessage
# Importa la excepción personalizada ChatServiceError para errores del servicio
from src.domain.exceptions import ChatServiceError
# Importa las interfaces de repositorio para acceder a datos de chat y productos
from src.domain.repositories import IChatRepository, IProductRepository


# CLASE 1: Interfaz para proveedores de modelos de lenguaje
class ILLMProvider(ABC):
    """Puerto/interfaz para proveedores de modelos de lenguaje (ej: Google Gemini, OpenAI)."""

    # Define un método abstracto que DEBE ser implementado por las subclases
    @abstractmethod
    def generate_response(
        self,
        current_message: str,  # El mensaje actual del usuario
        available_products: list,  # Lista de productos disponibles
        context: ChatContext,  # Contexto del chat (historial de mensajes)
    ) -> str:  # Retorna una cadena de texto (la respuesta del asistente)
        """Genera la respuesta del asistente basada en el contexto y productos disponibles."""


# CLASE 2: Servicio principal que coordina el flujo del chat
class ChatService:
    """Coordina el flujo del chat y la persistencia de datos."""

    # Método constructor que recibe las dependencias
    def __init__(
        self,
        product_repository: IProductRepository,  # Interfaz para acceder a productos de la BD
        chat_repository: IChatRepository,  # Interfaz para acceder a mensajes de la BD
        llm_provider: ILLMProvider,  # Proveedor de IA (Gemini, OpenAI, etc.)
    ) -> None:
        """Inicializa las dependencias del servicio.

        Args:
            product_repository: Interfaz del repositorio de productos.
            chat_repository: Interfaz del repositorio de chat.
            llm_provider: Puerto del proveedor de modelo de lenguaje.
        """
        # Guarda el repositorio de productos como atributo privado
        self._product_repository = product_repository
        # Guarda el repositorio de chat como atributo privado
        self._chat_repository = chat_repository
        # Guarda el proveedor de IA como atributo privado
        self._llm_provider = llm_provider

    # Método principal que procesa un mensaje de chat de principio a fin
    def process_message(self, session_id: str, message: str) -> tuple[str, datetime]:
        """Procesa una solicitud de chat de principio a fin.

        Flujo:
            1. Carga los productos disponibles.
            2. Carga el contexto reciente del chat.
            3. Genera la respuesta con el modelo de IA.
            4. Guarda los mensajes del usuario y asistente.
            5. Retorna la respuesta.

        Args:
            session_id: ID único de la sesión de conversación.
            message: Mensaje del usuario.

        Returns:
            tuple[str, datetime]: Tupla con (respuesta del asistente, marca de tiempo).

        Raises:
            ChatServiceError: Si el procesamiento falla.
        """
        # Envuelve el código en try-except para manejar errores
        try:
            # PASO 1: Obtiene TODOS los productos de la BD y filtra solo los que tienen stock > 0
            available_products = [p for p in self._product_repository.get_all() if p.stock > 0]
            # PASO 2: Obtiene los últimos 6 mensajes del chat para esta sesión desde la BD
            recent_messages = self._chat_repository.get_recent_messages(session_id=session_id, limit=6)
            # PASO 2: Crea un objeto ChatContext (contexto) a partir de los últimos 6 mensajes
            context = ChatContext.from_messages(recent_messages, limit=6)

            # PASO 3: Llama al proveedor de IA (Gemini) para generar la respuesta
            # Pasa: el mensaje actual, los productos disponibles y el contexto del chat
            response = self._llm_provider.generate_response(
                current_message=message,  # El mensaje que escribió el usuario
                available_products=available_products,  # Los zapatos disponibles
                context=context,  # El historial de los últimos 6 mensajes
            )

            # PASO 4a: Crea un objeto ChatMessage para el mensaje del usuario
            user_message = ChatMessage.create(role="user", content=message)
            # PASO 4b: Crea un objeto ChatMessage para la respuesta del asistente
            assistant_message = ChatMessage.create(role="assistant", content=response)
            # PASO 4c: Guarda el mensaje del usuario en la BD
            self._chat_repository.save_message(session_id, user_message)
            # PASO 4d: Guarda el mensaje del asistente en la BD
            self._chat_repository.save_message(session_id, assistant_message)

            # PASO 5: Retorna una tupla con la respuesta y la fecha/hora actual en UTC
            return response, datetime.now(timezone.utc)
        # Si ocurre cualquier error, lo captura en la variable 'exc'
        except Exception as exc:  # noqa: BLE001
            # Lanza una excepción personalizada ChatServiceError con un mensaje descriptivo
            raise ChatServiceError(f"Failed to process chat message: {exc}") from exc
