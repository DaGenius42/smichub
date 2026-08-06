from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.user.is_authenticated:
        return redirect('feed:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed:home')
    else:
        form = UserCreationForm()
    return render(request, 'registrations/signup.html', {'form': form})