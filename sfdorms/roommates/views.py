from django.shortcuts import render

# Create your views here.

def homepage(request):
    return render(request, 'roommates/index.html')

def about(request):
    return render(request, 'roommates/about.html')

def contact(request):
    return render(request, 'roommates/contact.html')