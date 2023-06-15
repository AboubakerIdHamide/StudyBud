from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomFrom

def loginUser(req):
    page='login'

    if req.user.is_authenticated:
        return redirect("home")

    if req.method=="POST":
        username=req.POST.get('username').lower()
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

    data={"page" : page}
    return render(req, 'base/login_register.html', data)

def registerUser(req):
    form=UserCreationForm()

    if req.method=="POST":
        form=UserCreationForm(req.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(req, user)
            return redirect("home")
        else:
            messages.error(req, "There was an error during registration process")


    data={"form" : form}
    return render(req, 'base/login_register.html', data)

def logoutUser(req):
    logout(req)
    return redirect("home")

def home(req):
    q=req.GET.get("q") if req.GET.get("q")!=None else ''
    rooms= Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
    )
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))

    data={
        "rooms": rooms,
        "topics": Topic.objects.all(),
        "room_count": rooms.count(),
        "room_messages":room_messages
    }
    return render(req, "base/home.html", data)

def room(req, pk):
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all()
    participants=room.participants.all()

    # add message
    if req.method=="POST":
        message=Message.objects.create(
            user=req.user,
            room=room,
            body=req.POST.get("body")
        )
        room.participants.add(req.user)
        return redirect("room", room.id)

    data={
        "room": room,
        "room_messages": room_messages,
        "participants":participants
    }
    return render(req, "base/room.html", data)

@login_required(login_url='login')
def createRoom(req):
    if req.method=="POST":
        form= RoomFrom(req.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    data={ 'form' : RoomFrom() }
    return render(req, "base/room_form.html", data)

@login_required(login_url='login')
def updateRoom(req, pk):
    room= Room.objects.get(id=pk)
    form= RoomFrom(instance=room)

    if req.user!=room.host:
        return HttpResponse("You're not allowed here")

    if req.method=="POST":
        form= RoomFrom(req.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")

    data={ 'form' : form }
    return render(req, "base/room_form.html", data)

@login_required(login_url='login')
def deleteRoom(req, pk):
    room= Room.objects.get(id=pk)

    if req.user!=room.host:
        return HttpResponse("You're not allowed here")

    if req.method=="POST":
        room.delete()
        return redirect('home')
    
    data={'obj':room}
    return render(req, "base/delete.html", data)

@login_required(login_url='login')
def deleteMessage(req, msgId, roomId):
    message= Message.objects.get(id=msgId)

    if req.user != message.user:
        return HttpResponse("You're not allowed here")

    if req.method=="POST":
        message.delete()
        return redirect('room', roomId)
    
    data={'obj':message}
    return render(req, "base/delete.html", data)