from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from .models import Comment, Room, TodoItem, Task, RoomMember
from .forms import ToDoItemForm, CommentForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.contrib import messages

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
    roommates = room.members.all()
    if request.user not in room.members.all():
        return HttpResponseForbidden("You are not a member of this room.")
    todos = room.todos.prefetch_related('comments__user')

    if request.method == 'POST' and 'comment-task-id' in request.POST:
        task_id = request.POST.get('comment-task-id')
        task = get_object_or_404(TodoItem, id=task_id, room=room)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('room_detail', room_id=room.id)
        
    comment_form = CommentForm()
    return render(request, 'roommates/room_detail.html', {
        'room': room, 
        'todos': todos, 
        'comment_form': comment_form,
        'roommates': roommates
    })

@login_required
def add_todo(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.user not in room.members.all():
        return HttpResponseForbidden("You are not a member of this room.")
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            TodoItem.objects.create(room=room, text=text, created_by=request.user)
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
            RoomMember.objects.get_or_create(user=user, room=room)
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

@login_required
def add_comment(request, todo_id):
    if request.method == 'POST':
        todo = get_object_or_404(TodoItem, id=todo_id)
        text = request.POST.get('text')
        if text:
            comment = Comment.objects.create(todo=todo, user=request.user, text=text)
            html = render_to_string('roommates/comment.html', {'comment': comment})
            return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        comment.delete()
        return  JsonResponse({"success": True})
    return JsonResponse({"success": False, 'error': 'Not authorized'}, status=403) 

def mark_todo_done(request, todo_id):
    todo = get_object_or_404(TodoItem, id = todo_id)
    if request.method == 'POST':
        todo.is_done = True
        todo.save()
    return redirect('room_detail', room_id=todo.room.id)

def room_dashboard(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    members = room.roommember_set.all().order_by('-points')
    tasks = Task.objects.filter(room=room)
    return render(request, 'roommates/dashboard.html', {
        'room': room,
        'members': members,
        'tasks': tasks
    })

def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not task.is_completed:
        task.is_completed = True
        task.completed_by = request.user
        task.save()

        room_member, created = RoomMember.objects.get_or_create(
            user=request.user, 
            room=task.room
        )
        room_member.points += 10
        room_member.save()

    return redirect('room_dashboard', room_id=task.room.id)

@require_GET
def room_members_partial(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    members = room.roommember_set.all()
    return render(request, 'partials/members.list.html', {'members': members})

@login_required
def add_task(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Verify user is a room member
    if not room.members.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You're not a member of this room")
    
    if request.method == "POST":
        # Fix typo in 'description' parameter
        description = request.POST.get('description')  # Changed from 'descripstion'
        
        if description:
            # Create task with logged-in user as creator
            Task.objects.create(
                room=room,
                description=description,
                created_by=request.user  # Add creator tracking
            )
            messages.success(request, "Task created successfully!")
        else:
            messages.error(request, "Task description cannot be empty")
    
    return redirect('room_dashboard', room_id=room.id)

@login_required
def create_task(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        description = request.POST.get()