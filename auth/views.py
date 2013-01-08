from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from decorators import login_required
from forms import UserForm
from music.models import Instrument

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
                url = request.GET.get('next', reverse('section_home'))
                return HttpResponseRedirect(url)
    else:
        form = AuthenticationForm()
    c = {'form': form, 'next': request.GET.get('next')}
    c = RequestContext(request, c)
    return render_to_response("auth/login.html", c)

def logout_view(request):
    """Logout view
    """
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def profile(request):
    user = request.user
    if request.POST:
        if request.POST.get('is_user_form') is not None:
            user_form = UserForm(instance=user, data=request.POST)
            if user_form.is_valid():
                user_form.save()
                msg = _('Your changes were successfully saved.')
                messages.add_message(request, messages.SUCCESS, msg)
                return HttpResponseRedirect(reverse('profile'))
            else:
                msg = _('Please fix the errors below.')
                messages.add_message(request, messages.ERROR, msg)
            password_form = PasswordChangeForm(user)
        elif request.POST.get('is_change_password_form') is not None:
            password_form = PasswordChangeForm(user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                msg = _('Your password was successfully changed.')
                messages.add_message(request, messages.SUCCESS, msg)
                return HttpResponseRedirect(reverse('profile'))
            else:
                msg = _('Please fix the errors below.')
                messages.add_message(request, messages.ERROR, msg)
            user_form = UserForm(instance=user)
        else:
            user_form = UserForm(instance=user)
            password_form = PasswordChangeForm(user)

    else:
        user_form = UserForm(instance=user)
        password_form = PasswordChangeForm(user)
    ids = user.instruments.all().values_list('instrument__id', flat=True)
    c = {
        'user': user,
        'user_form': user_form,
        'password_form': password_form,
        'instruments': Instrument.objects.all().exclude(id__in=ids)
    }
    c = RequestContext(request, c)
    return render_to_response("auth/profile.html", c)