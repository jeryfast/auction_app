from rest_framework import serializers
from .models import Auction, Bid

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'name', 'description', 'image', 'starting_price', 'is_active', 'start_time', 'end_time', 'creator']
        extra_kwargs = {
            'creator': {'read_only': True}  # Make creator read-only so it's not expected in the input
        }

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'user', 'amount', 'timestamp']
