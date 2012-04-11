from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def login_view(request):
    """Login view
    """
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        c = RequestContext(request, {'form': form})
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'],
                                password=data['password'])
            if user is not None and user.is_active:
                login(request, user)
                return HttpResponseRedirect("/")
    else:
        form = AuthenticationForm()
    c = RequestContext(request, {'form': form})
    return render_to_response("auth/login.html", c)

def logout_view(request):
    """Logout view
    """
    logout(request)
    return HttpResponseRedirect("/")
