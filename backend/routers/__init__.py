from .health import router as health_router
from .horoscope import router as horoscope_router
from .tarot import router as tarot_router
from .astronomy import router as astronomy_router

__all__ = [
    "health_router",
    "horoscope_router",
    "tarot_router",
    "astronomy_router"
]
