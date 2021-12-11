from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.messages import get_messages
from django.contrib import messages
from .models import *
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


def index(request):
    return render(request, "index.html")


def register(request):
    # print(request.POST)
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        errors = User.objects.basic_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/")

        else:

            request.POST['email']

            hashed = bcrypt.hashpw(
                request.POST['password'].encode(), bcrypt.gensalt())
            decoded_hash = hashed.decode('utf-8')

            user = User.objects.create(
                email=request.POST['email'], password=decoded_hash)
            request.session['u_id'] = user.id
            messages.success(request, "User successfully added")
            return render(request, "login.html")


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    user_list = User.objects.filter(email=request.POST['email'])
    if not user_list:
        messages.error(request, "Invalid credentials!")
        return render(request, 'login.html')
    user = user_list[0]

    if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        request.session['login'] = True
        request.session['u_id'] = user.id
        request.session['u_email'] = user.email

        return render(request, 'success.html')
    else:
        messages.error(request, "Invalid credentials!")
        return render(request, 'login.html')


def logout(request):
    request.session.clear()
    messages.info(request, "Logged out successfully!")
    return redirect('/')

#################################################################################################


def users(request, user_id):
    author = User.objects.get(id=user_id)
    context = {
        'quotes': Quote.objects.filter(author=author),
        'author': author
    }
    return render(request, "users.html", context)


def quotes(request):
    registered_users = User.objects.all()
    current_user = User.objects.get(id=request.session['u_id'])
    favourites = Quote.objects.filter(favouriting_users=current_user)
    allquotes = Quote.objects.all().order_by(
        '-id').exclude(id__in=[f.id for f in favourites])
    context = {
        "registered_users": registered_users,
        "current_user": current_user,
        "quotes": allquotes,
        "favourites": favourites
    }

    return render(request, "quotes_list.html", context)


def quote_post(request):
    if request.method == "GET":
        return redirect('/quotes_list')
    if request.method == "POST":
        quote_text = request.POST['quote']
        user_id = request.session['u_id']
        quoted_by = request.POST['quote_author']

        result = Quote.objects.validate_quote(quote_text, user_id, quoted_by)
        if result['status'] == True:
            messages.info(request, result['errors'])
            return redirect('/quotes_list')
        messages.error(request, result['errors'], extra_tags="quote_post")
        return redirect('/quotes_list')


def add_favorite_for_current_user(request, quote_id):
    user_id = request.session['u_id']
    Quote.objects.add_favourite_for_user(user_id, quote_id)
    return redirect('/quotes_list')


def remove_from_favourites(request, quote_id):
    user_id = request.session['u_id']
    Quote.objects.remove_from_favorites(user_id, quote_id)
    return redirect('/quotes_list')


def dashboard(request):
    return redirect('/quotes_list')

#################################################################################################


def edit_quote(request, quote_id):

    thisQuote = Quote.objects.get(id=quote_id)
    if request.method == 'GET':
        data = {
            "thisQuote": thisQuote
        }
        return render(request, "edit_quote.html", data)

    else:
        request.method == 'POST'
        thisQuote.user_id = request.session['u_id']
        thisQuote.quote_text = request.POST['quote']
        thisQuote.quoted_by = request.POST['quote_author']
        result = Quote.objects.validate_quote(
            thisQuote.quote_text, thisQuote.user_id, thisQuote.quoted_by)

        if result['status'] == True:
            messages.info(request, result['errors'])
            return redirect('/quotes_list')

        if request.method == 'POST':
            thisQuote.user_id = request.session['u_id']
            thisQuote.quote_text = request.POST['quote']
            thisQuote.quoted_by = request.POST['quote_author']
            result = Quote.objects.validate_quote(
                thisQuote.quote_text, thisQuote.user_id, thisQuote.quoted_by)
            messages.error(request, result['errors'], extra_tags="quote_post")
            return redirect('/quotes_list')

        messages.success(request, "Quote successfully updated")
        """ return redirect('/quotes_list') """
        return redirect("/edit/"+str(thisQuote.quote_id))
