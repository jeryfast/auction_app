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
        if not self.is_active:
            try:
                winner = self.get_winner()
                highest_bid = self.bids.order_by('-amount').first()

                if winner:
                    # Notify auction winner using Anymail
                    winner_message = AnymailMessage(
                        subject="Congratulations! You've won the auction!",
                        body=f'Hi {winner.username}, you have won the auction "{self.name}"!',
                        from_email=config('SENDGRID_FROM'),
                        to=[winner.email],
                    )
                    winner_message.send()
                
              
                # Notify auction creator about auction completion and winner
                subject="Your auction has ended",
                body=(
                        f'Hi {self.creator.username}, your auction "{self.name}" has ended.\n'
                        f'The winner is {winner.username} with a bid of {highest_bid.amount}.\n'
                        if winner else 'No one placed a bid.'
                    ),
                from_email=config('SENDGRID_FROM'),
                to=[self.creator.email],
                creator_message = AnymailMessage(
                    subject="Your auction has ended",
                    body=(
                        f'Hi {self.creator.username}, your auction "{self.name}" has ended.\n'
                        f'The winner is {winner.username} with a bid of {highest_bid.amount}.\n'
                        if winner else 'No one placed a bid.'
                    ),
                    from_email=config('SENDGRID_FROM'),
                    to=[self.creator.email],
                )
                print(body)
                print(from_email, to)
                
                creator_message.send()
            except AnymailAPIError as e:
                # Log the detailed error message
                print(f"Anymail API Error: {e}")

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
