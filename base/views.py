from django.shortcuts import render


rooms=[
    {"id":1, "name":"Learn Python"},
    {"id":2, "name":"Learn PHP"},
    {"id":3, "name":"Learn Django"},
    {"id":4, "name":"Learn Laravel"},
]

def home(req):
    data={"rooms":rooms}
    return render(req, "base/home.html", data)

def room(req, pk):
    matchedRoom=None
    for i in rooms:
        if i["id"]==int(pk):
            matchedRoom=i
    data={"room":matchedRoom}
    return render(req, "base/room.html", data)
