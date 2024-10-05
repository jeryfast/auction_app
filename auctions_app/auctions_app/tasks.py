# auctions_app/tasks.py
from celery import shared_task
from anymail.message import AnymailMessage
from decouple import config  # To use environment variables

@shared_task
def send_auction_winner_email(winner_email, winner_username, auction_name):
    subject = "Congratulations! You've won the auction!"
    body = f'Hi {winner_username}, you have won the auction "{auction_name}"!'
    
    email = AnymailMessage(
        subject=subject,
        body=body,
        from_email=config('SENDGRID_FROM'),
        to=[winner_email],
    )
    email.send()

@shared_task
def send_auction_creator_email(creator_email, creator_username, auction_name, winner_username, highest_bid_amount):
    subject = "Your auction has ended"
    body = (
        f'Hi {creator_username}, your auction "{auction_name}" has ended.\n'
        f'The winner is {winner_username} with a bid of {highest_bid_amount}.'
    )
    
    email = AnymailMessage(
        subject=subject,
        body=body,
        from_email=config('SENDGRID_FROM'),
        to=[creator_email],
    )
    email.send()
