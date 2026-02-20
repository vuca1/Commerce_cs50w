from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from decimal import Decimal

from .models import User, AuctionListing, Bid, Category, Comment


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


def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        initial_price = Decimal(request.POST["price"])
        image_url = request.POST.get("image_url")
        category_id = request.POST.get("category")

        category = None
        if category_id:
            category = Category.objects.get(id=category_id)

        new_listing = AuctionListing(title=title, description=description, initial_price=initial_price, image_url=image_url, category=category, creator=request.user)
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))


    return render(request, "auctions/create_listing.html", {
        "categories": Category.objects.all()
    })
        
def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            new_comment = Comment(content=content, author=request.user, item=listing)
            new_comment.save()

        return redirect("listing", listing_id=listing_id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.order_by("created_at")
    })