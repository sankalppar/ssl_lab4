from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from github_profiles_app.models import Profile, Repository
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            response = requests.get("https://api.github.com/users/" + form.cleaned_data['username'])
            if response.ok:
                new_user = form.save()
                profile_data = response.json()
                prof = Profile(user=new_user, follow_count=profile_data['followers'], last_update=profile_data['updated_at'])
                prof.save()
                response = requests.get("https://api.github.com/users/" + form.cleaned_data['username'] + "/repos")
                repo_data = response.json()
                for repo in repo_data:
                    new_repo = Repository(name=repo['name'],creator=prof,num_star=repo['stargazers_count'])
                    new_repo.save()
                new_user = authenticate(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        )
                login(request, new_user)
                return redirect('/profile')
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})

def get_user_profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    repositories = Repository.objects.filter(creator=profile)
    return render(request, 'user_profile.html', {"user":user, "profile":profile, "repositories":repositories})

def profile(request):
    return HttpResponseRedirect(reverse(get_user_profile, args=[request.user.username]))

def explore(request):
    all_profiles = User.objects.all()
    return render(request, 'explore.html', {"profiles":all_profiles})

def update_user(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    repositories = Repository.objects.filter(creator=profile)
    response = requests.get("https://api.github.com/users/" + username)
    if response.ok:
        profile_data = response.json()
        profile.follow_count = profile_data['followers']
        profile.last_update = profile_data['updated_at']
        profile.save()
        response = requests.get("https://api.github.com/users/" + username + "/repos")
        repo_data = response.json()
        for repo in repo_data:
            x = Repository.objects.filter(name=repo['name']).count()
            if x:
                saved_repo = Repository.objects.filter(name=repo['name'])
                saved_repo.update(num_star=repo['stargazers_count'])
                for item in saved_repo:
                    item.save()
                #saved_repo.num_star = repo['stargazers_count']
                #saved_repo.save()
            else:
                new_repo = Repository(name=repo['name'],creator=profile,num_star=repo['stargazers_count'])
                new_repo.save()
    return HttpResponseRedirect(reverse(get_user_profile, args=[username]))
