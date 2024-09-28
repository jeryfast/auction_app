from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Auction(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='auction_images/')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    
    @property
    def end_time(self):
        return self.start_time + timedelta(days=1)
    
    @property
    def is_active(self):
        return timezone.now() < self.end_time

    def __str__(self):
        return self.name

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']  # Highest bid first

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
