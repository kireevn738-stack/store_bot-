from .start import router as start_router
from .registration import router as registration_router
from .language import router as language_router
from .store import router as store_router
from .products import router as products_router
from .categories import router as categories_router
from .orders import router as orders_router
from .analytics import router as analytics_router

routers = [
    start_router,
    registration_router,
    language_router,
    store_router,
    products_router,
    categories_router,
    orders_router,
    analytics_router
]

__all__ = [
    'start_router',
    'registration_router',
    'language_router',
    'store_router',
    'products_router',
    'categories_router',
    'orders_router',
    'analytics_router',
    'routers'
]
