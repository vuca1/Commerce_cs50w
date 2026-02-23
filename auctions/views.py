from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django import forms

from decimal import Decimal

from .models import User, AuctionListing, Bid, Category, Comment

class ListingForm(forms.Form):
    title = forms.CharField(
        label="Title",
        required=True,
        max_length=50
    )
    description = forms.CharField(
        label="Description",
        required=True,
        max_length=500,
        widget=forms.Textarea
    )
    initial_price = forms.DecimalField(
        label="Initial price",
        min_value=0,
        required=True
    )
    image_url = forms.URLField(
        label="Image URL",
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select category"
    )

class CommentForm(forms.Form):
    content = forms.CharField(
        label="Comment",
        required=True
    )

def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.filter(is_active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            initial_price = form.cleaned_data["initial_price"]
            image_url = form.cleaned_data["image_url"]
            category_id = form.cleaned_data["category"]
        else:
            return render(request, "auctions/create_listing.html", {
                "categories": Category.objects.all(),
                "form": form
            })

        category = None
        if category_id:
            category = Category.objects.get(id=category_id)

        new_listing = AuctionListing(
            title=title,
            description=description,
            initial_price=initial_price, 
            image_url=image_url,
            category=category,
            creator=request.user)
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))


    return render(request, "auctions/create_listing.html", {
        "categories": Category.objects.all(),
        "form": ListingForm()
    })
        
def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": listing.comments.order_by("created_at"),
                "form": form
            })

        new_comment = Comment(content=content, author=request.user, item=listing)
        new_comment.save()
        return redirect("listing", listing_id=listing_id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.order_by("created_at"),
        "form": CommentForm()
    })