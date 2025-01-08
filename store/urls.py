from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dialogflow-query/', views.dialogflow_query, name='dialogflow_query'),
]

