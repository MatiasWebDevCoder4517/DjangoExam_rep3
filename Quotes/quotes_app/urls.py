from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('main', views.register),
    path('login', views.login),
    path('logout', views.logout),

    path('quotes_list', views.quotes),
    path('quote', views.quote_post),
    path('quote/<int:quote_id>', views.add_favorite_for_current_user),
    path('remove/<int:quote_id>', views.remove_from_favourites),
    path('users/<int:user_id>', views.users),
    path('dashboard', views.dashboard),
    path('edit/<int:quote_id>', views.edit_quote),




]


'''
path('edit/<int:quote_id>', views.edit),
'''
