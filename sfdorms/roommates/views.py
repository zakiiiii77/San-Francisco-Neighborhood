from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

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