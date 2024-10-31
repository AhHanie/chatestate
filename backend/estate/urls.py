from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload", views.upload_excel, name="upload_excel"),
    path("query", views.process_nlp_query, name="process_nlp_query"),
]
