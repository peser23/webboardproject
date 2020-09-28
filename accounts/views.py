from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('home'))
    elif request.method == 'GET':
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


