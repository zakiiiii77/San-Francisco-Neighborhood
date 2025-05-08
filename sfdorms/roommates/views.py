import os
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Comment, Room, Task, RoomMember
from .forms import TaskForm, CommentForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
import spotify
from spotipy.oauth2 import SpotifyOAuth

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
    tasks = room.tasks.prefetch_related('comments__user')

    if request.method == 'POST' and 'comment-task-id' in request.POST:
        task_id = request.POST.get('comment-task-id')
        task = get_object_or_404(Task, id=task_id, room=room)
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
        'tasks': tasks, 
        'comment_form': comment_form,
        'roommates': roommates
    })

@login_required
def add_task(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        description = request.POST.get('description')
        if description:
            Task.objects.create(
                room=room,
                description=description,
                created_by=request.user
            )
    return redirect('room_detail', room_id=room_id)

@login_required
def edit_task(request, room_id, task_id):
    task = get_object_or_404(Task, id=task_id, room__id=room_id)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        task.description = request.POST.get('description')
        task.save()
        return redirect('room_detail', room_id=room_id)
    return render(request, "roommates/edit_task.html", {"task":task, "room_id": room_id})

@login_required
def delete_task(request, room_id, task_id):
    task = get_object_or_404(Task, id=task_id, room_id=room_id)
    if request.method == "POST":
        task.delete()
        return redirect('room_detail', room_id=room_id)

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

def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        comment_text = request.POST.get('text')
        Comment.objects.create(
            task=task,
            text=comment_text,
            user=request.user
        )
        
    return redirect('room_detail', room_id=task.room.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        comment.delete()
        return  JsonResponse({"success": True})
    return JsonResponse({"success": False, 'error': 'Not authorized'}, status=403) 

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id = task_id)
    if request.method == 'POST':
        task.is_completed = True
        task.save()
    return redirect('room_detail', room_id=task.room.id)

@login_required
def room_dashboard(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    members = room.roommember_set.all().order_by('-points')
    tasks = Task.objects.filter(room=room)
    return render(request, 'roommates/dashboard.html', {
        'room': room,
        'members': members,
        'tasks': tasks
    })

@login_required
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

def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('aad186414a0e4471a2282d36316f31a8'),
        client_secret=os.getenv('5648336dd6514605b3a28ee73796f7ec'),
        redirect_uri=os.getenv('http://127.0.0.1:8000/spotify/callback/'),
        scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('aad186414a0e4471a2282d36316f31a8'),
        client_secret=os.getenv('5648336dd6514605b3a28ee73796f7ec'),
        redirect_uri=os.getenv('http://127.0.0.1:8000/spotify/callback/')
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    request.session['token_info'] = token_info
    return redirect('your_redirect_url')  # Replace with your redirect URL after authentication

