from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from anymail.message import AnymailMessage
from anymail.exceptions import AnymailAPIError
from decouple import config  # To use environment variables
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .tasks import send_auction_winner_email, send_auction_creator_email

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

    def get_winner(self):
        # Get the highest bid and the associated user (winner)
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.user if highest_bid else None
    
    def end_auction(self):
        winner = self.get_winner()
        highest_bid = self.bids.order_by('-amount').first()

        print(f"Dispatching email to {winner.email}")
        print(f"Dispatching email to {self.creator.email}")

        if winner:
            # Send email to winner asynchronously
            winner_task = send_auction_winner_email.delay(
                winner_email=winner.email,
                winner_username=winner.username,
                auction_name=self.name
            )

        # Send email to creator asynchronously
        creator_task = send_auction_creator_email.delay(
            creator_email=self.creator.email,
            creator_username=self.creator.username,
            auction_name=self.name,
            winner_username=winner.username if winner else "No one",
            highest_bid_amount=highest_bid.amount if winner else "No bids"
        )

        return winner_task, creator_task

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
