from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Room, TodoItem
from .forms import ToDoItemForm
from django.contrib.auth.models import User

# Create your views here.

def homepage(request):
    return render(request, 'roommates/index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid ():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'roommates/signup.html', {'form': form})

def about(request):
    return render(request, 'roommates/about.html')

def contact(request):
    return render(request, 'roommates/contact.html')

@login_required
def room_list(request):
    rooms = Room.objects.filter(members=request.user)
    return render(request, 'roommates/room_list.html', {'rooms': rooms})

@login_required
def create_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            room = Room.objects.create(name=name)
            room.members.add(request.user)
            return redirect('room_detail', room_id=room.id)
    return render(request, 'roommates/create_room.html')

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.user not in room.members.all():
        return HttpResponseForbidden("You are not a member of this room.")
    todos = room.todos.all()
    return render(request, 'roommates/room_detail.html', {'room': room, 'todos': todos})

@login_required
def add_todo(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.user not in room.members.all():
        return HttpResponseForbidden("You are not a member of this room.")
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            TodoItem.objects.create(room=room, text=text)
    return redirect('room_detail', room_id=room.id)

@login_required
def edit_todo(request, room_id, todo_id):
    todo = get_object_or_404(TodoItem, id=todo_id, room__id=room_id)
    if request.method == "POST":
        form = ToDoItemForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("room_detail", room_id=room_id)
    else:
        form = ToDoItemForm(instance=todo)
    return render(request, "roommates/edit_todo.html", {"form": form, "room_id": room_id})

@login_required
def delete_todo(request, room_id, todo_id):
    todo = get_object_or_404(TodoItem, id=todo_id, room__id=room_id)
    if request.method == "POST":
        todo.delete()
        return redirect("room_detail", room_id=room_id)
    return render(request, "roommates/delete_confirm.html", {"todo": todo, "room_id": room_id})

@login_required
def add_member(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username).first()
        if user:
            room.members.add(user)
            room.save()
        return redirect("room_detail", room_id=room_id)
    return render(request, "roommates/add_member.html", {"room": room})

@login_required
def remove_member(request, room_id, user_id):
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        room.members.remove(user)
        room.save()
        return redirect("room_detail", room_id=room_id)
    return render(request, "roommates/remove_confirm.html", {"user": user, "room": room})

@login_required
def room_detail_api(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, "roommates/todo_list_partial.html", {"room": room})