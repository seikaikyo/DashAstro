from .health import router as health_router
from .horoscope import router as horoscope_router
from .tarot import router as tarot_router
from .astronomy import router as astronomy_router
from .compatibility import router as compatibility_router
from .stats import router as stats_router
from .lucky_days import router as lucky_days_router
from .sukuyodo import router as sukuyodo_router

__all__ = [
    "health_router",
    "horoscope_router",
    "tarot_router",
    "astronomy_router",
    "compatibility_router",
    "stats_router",
    "lucky_days_router",
    "sukuyodo_router"
]
