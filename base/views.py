from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Room, Topic, Message, User
from .forms import RoomFrom, UserForm, MyUserCreationForm

def loginUser(req):
    page='login'

    if req.user.is_authenticated:
        return redirect("home")

    if req.method=="POST":
        email=req.POST.get('email').lower()
        password=req.POST.get('password')
        try:
            user= User.objects.get(email=email)
        except:
            messages.error(req, 'User does not exists')
        
        user=authenticate(req, email=email, password=password)
        if user is not None:
            login(req, user)
            return redirect("home")
        else:
            messages.error(req, 'Invalid credentials !')

    data={"page" : page}
    return render(req, 'base/login_register.html', data)

def registerUser(req):
    form=MyUserCreationForm()

    if req.method=="POST":
        form=MyUserCreationForm(req.POST)
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

@login_required(login_url='login')
def updateUser(req):
    user=req.user
    form=UserForm(instance=user)

    if req.method=="POST":
        form=UserForm( req.POST, req.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    data={ 'form':form }
    return render(req, "base/update-user.html", data)

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
        "topics": Topic.objects.all()[0:5],
        "room_count": rooms.count(),
        "room_messages":room_messages
    }
    return render(req, "base/home.html", data)

def topicsPage(req):
    q=req.GET.get("q") if req.GET.get("q")!=None else ''
    data={ 'topics': Topic.objects.filter(name__icontains=q) }
    return render(req, "base/topics.html", data)

def activitiesPage(req):
    room_messages=Message.objects.all()
    data={ "room_messages":room_messages }
    return render(req, "base/activity.html", data)

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

def userProfile(req, pk):
    user= User.objects.get(id=pk)
    rooms= user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    data={ 
        "user": user,
        "rooms": rooms,
        "topics":topics,
        "room_messages":room_messages
    }
    return render(req, "base/profile.html", data)

@login_required(login_url='login')
def createRoom(req):
    if req.method=="POST":
        topic_name= req.POST.get("topic")
        topic, created= Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=req.user,
            topic=topic,
            name=req.POST.get("name"),
            description=req.POST.get("description"),
        )
        return redirect("home")

    data={
         'form' : RoomFrom(),
         'topics' : Topic.objects.all(),
    }
    return render(req, "base/room_form.html", data)

@login_required(login_url='login')
def updateRoom(req, pk):
    room= Room.objects.get(id=pk)
    form= RoomFrom(instance=room)

    if req.user!=room.host:
        return HttpResponse("You're not allowed here")

    if req.method=="POST":
        topic_name= req.POST.get("topic")
        topic, created= Topic.objects.get_or_create(name=topic_name)
        room.topic= topic
        room.name= req.POST.get("name")
        room.description= req.POST.get("description")
        room.save()
        return redirect("home")

    data={ 
        'form' : form,
        'topics' : Topic.objects.all(),
        'room':room
    }
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