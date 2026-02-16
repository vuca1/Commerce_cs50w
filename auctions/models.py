from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name} - {self.description}"

class AuctionListing(models.Model):
    name = models.CharField(max_length=64)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="displayed_items")
    initial_price = models.FloatField()
    current_price = models.FloatField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.is_active:
            return f"{self.name} available. Current price: {self.current_price}."
        else:
            return f"Listing {self.name} no longer available."

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.FloatField()
    time = models.DateTimeField()
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bidder} - {self.item.name}: {self.amount}"

class Comment(models.Model):
    content = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.item}: {self.author} - {self.content}"

