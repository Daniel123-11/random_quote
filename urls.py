from django.urls import path
from . import views
app_name = 'quotes'
urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_quote, name='submit'),
    path('popular/', views.popular, name='popular'),
    path('vote/<int:pk>/<str:action>/', views.vote, name='vote'),
]
