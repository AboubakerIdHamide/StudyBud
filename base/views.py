from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Room, Topic
from .forms import RoomFrom

def loginView(req):
    if req.method=="POST":
        username=req.POST.get('username')
        password=req.POST.get('password')
        try:
            user= User.objects.get(username=username)
        except:
            messages.error(req, 'User does not exists')
        
        user=authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            return redirect("home")
        else:
            messages.error(req, 'Invalid credentials !')
    data={}
    return render(req, 'base/login_register.html', data)

def home(req):
    q=req.GET.get("q") if req.GET.get("q")!=None else ''
    rooms= Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
    )

    data={
        "rooms": rooms,
        "topics": Topic.objects.all(),
        "room_count": rooms.count()
    }
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

