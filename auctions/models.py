from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.exceptions import ValidationError
from decimal import Decimal


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "AuctionListing",
        blank=True,
        related_name="watchlisted_by"
    )

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name}"

class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    image_url = models.URLField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="displayed_items")
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_active:
            return f"{self.title} available. Current price: {self.current_price:,} €"
        else:
            return f"Listing {self.title} no longer available."
        
    @property
    def current_price(self):
        highest_bid = self.bids.order_by("-amount").first()
        if highest_bid:
            return highest_bid.amount
        else:
            return self.initial_price
        
    @property
    def highest_bidder(self):
        highest_bid = self.bids.order_by("-amount").first()
        return highest_bid.bidder if highest_bid else None

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bidder} - {self.item.name}: {self.amount}"

    def clean(self):
        if self.amount <= self.item.current_price:
            raise ValidationError(f"Bid must be higher than current price ({self.item.current_price}).")

class Comment(models.Model):
    content = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item}: {self.author} - {self.content}"
