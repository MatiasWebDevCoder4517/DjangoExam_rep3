from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, date
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.


class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}

        if len(postData['password']) < 8:
            errors["password"] = "Password must be a minimum length of eight characters!"

        if postData['password'] != postData['confirm_password']:
            errors["password"] = "Passwords must match!"

        if len(postData['email']) < 7:
            errors["email"] = "Email should be at least 4 or more characters"

        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Email must be a valid email address!"

        return errors


class User(models.Model):
    email = models.EmailField(
        max_length=100, default="user_email123@gmail.com")
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):
        return self.email
##################################################################################


class QuoteManager(models.Manager):
    def validate_quote(self, quote_text, user_id, quoted_by):
        errors = []

        if len(quoted_by) < 4:
            msg = "'Quoted by' should be not be less than 4 characters."
            errors.append(msg)
            result = {'status': False, 'errors': errors[0]}
            return result
        elif len(quote_text) < 10:
            msg = "Quote is too short to be a quote!"
            errors.append(msg)
            result = {'status': False, 'errors': errors[0]}
            return result
        current_user = User.objects.get(id=user_id)
        self.create(quote_text=quote_text,
                    author=current_user, quoted_by=quoted_by)
        msg = "Quote created."
        errors.append(msg)
        result = {'status': True, 'errors': errors[0]}
        return result

    def add_favourite_for_user(self, user_id, quote_id):
        quote = Quote.objects.get(id=quote_id)
        current_user = User.objects.get(id=user_id)
        quote.favouriting_users.add(current_user)
        result = {'status': True}
        return result

    def remove_from_favorites(self, user_id, quote_id):
        quote = Quote.objects.get(id=quote_id)
        current_user = User.objects.get(id=user_id)
        quote.favouriting_users.remove(current_user)


class Quote(models.Model):
    quote_text = models.TextField(max_length=1000, null=True)
    author = models.ForeignKey(
        User, related_name="quotes_posted", on_delete=models.CASCADE)
    favouriting_users = models.ManyToManyField(
        User, related_name="favourite_quotes")
    quoted_by = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuoteManager()
