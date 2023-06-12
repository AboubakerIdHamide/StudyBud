from django.shortcuts import render, redirect
from .models import Room
from .forms import RoomFrom

def home(req):
    data={"rooms": Room.objects.all()}
    return render(req, "base/home.html", data)

def room(req, pk):
    data={"room": Room.objects.get(id=pk)}
    return render(req, "base/room.html", data)

def createRoom(req):
    if req.method=="POST":
        form= RoomFrom(req.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    data={ 'form' : RoomFrom() }
    return render(req, "base/room_form.html", data)

def updateRoom(req, pk):
    room= Room.objects.get(id=pk)
    form= RoomFrom(instance=room)

    if req.method=="POST":
        form= RoomFrom(req.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")

    data={ 'form' : form }
    return render(req, "base/room_form.html", data)

def deleteRoom(req, pk):
    room= Room.objects.get(id=pk)

    if req.method=="POST":
        room.delete()
        return redirect('home')
    
    data={'obj':room}
    return render(req, "base/delete.html", data)

