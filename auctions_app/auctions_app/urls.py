from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet, BidViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import redis_ping

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet)
router.register(r'bids', BidViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  # Include the admin URLs here
    path('', include(router.urls)),   # Include your API router
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('redis-ping/', redis_ping, name='redis_ping'),
]
