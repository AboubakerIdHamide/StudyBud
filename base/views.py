from django.shortcuts import render
from .models import Room

def home(req):
    data={"rooms": Room.objects.all()}
    return render(req, "base/home.html", data)

def room(req, pk):
    data={"room": Room.objects.get(id=pk)}
    return render(req, "base/room.html", data)
