from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("hello/", views.hello_template, name="hello_template"),
    path("upload/", views.upload_file, name="upload_file"),
]
