import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message
from config import ALLOWED_USERS

logger = logging.getLogger(__name__)

async def check_authorization(
  handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
  event: Message,
  data: Dict[str, Any]
) -> Any:
  if ALLOWED_USERS and event.from_user.id not in ALLOWED_USERS:
    await event.answer("❌ No tienes permiso para usar este bot.")
    logger.warning(f"Usuario no autorizado: {event.from_user.id} (@{event.from_user.username})")
    return
  
  return await handler(event, data)
