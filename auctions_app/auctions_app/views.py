from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Auction, Bid
from .serializers import AuctionSerializer, BidSerializer
from django.utils import timezone
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def redis_ping(request):
    try:
        channel_layer = get_channel_layer()
        # Ping Redis by sending a test message to the channel layer
        async_to_sync(channel_layer.send)('test_channel', {'type': 'ping.message'})
        return JsonResponse({"status": "Redis is working!"})
    except Exception as e:
        return JsonResponse({"status": "Redis connection failed", "error": str(e)}, status=500)
    
    

class AuctionPagination(PageNumberPagination):
    page_size = 2  # Default number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    pagination_class = AuctionPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['starting_price', 'name']
    
    # Restrict POST to authenticated users
    def get_permissions(self):
        if self.action == 'create':  # 'create' is for POST requests
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Set the `creator` to the currently authenticated user
        serializer.save(creator=self.request.user)
    
    def get_queryset(self):
        # Filter by keyword if provided
        queryset = Auction.objects.all()
        keyword = self.request.query_params.get('keyword', None)
        if keyword is not None:
            queryset = queryset.filter(name__icontains=keyword)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bid(self, request, pk=None):
        auction = self.get_object()
        if not auction.is_active:
            return Response({"error": "Auction is closed."}, status=400)

        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Bid amount is required."}, status=400)

        Bid.objects.create(auction=auction, user=request.user, amount=amount)
        return Response({"message": "Bid placed successfully."})
        

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
