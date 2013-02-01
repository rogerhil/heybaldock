from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
                        HttpResponse
from django.template import loader
from django.template import Context
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from forms import ContactForm
from lib.decorators import ajax
from hbauth.decorators import login_required
from models import Notification, UserNotification
from section.views import section_view


@require_POST
def send_mail(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        msg = _('Your message has been successfully sent')
        messages.add_message(request, messages.SUCCESS, msg)
        url = reverse('section_view', args=('contato',))
        return HttpResponseRedirect(url)
    else:
        return section_view(request, slug='contato')

@ajax
@login_required
@require_POST
def notify(request, app, model, id, action):
    band = request.band
    ct = ContentType.objects.get(app_label=app, model=model)
    try:
        obj = ct.get_object_for_this_type(id=id)
    except:
        message = _("%s with id %s does not exist" % (model, id))
        return dict(success=False, message=message)
    users = band.active_members
    print request.POST
    notes = request.POST.get('notes') or None
    mail = request.POST.get('mail') or False
    Notification.notify(obj, action, users, notes=notes, mail=mail)
    return dict(success=True)

@ajax
@login_required
def my_notifications(request):
    user = request.user
    notifications = user.notifications.all().order_by('-notification__date')
    context = dict(notifications=notifications, user=user)
    template = loader.get_template("contact/my_notifications.html")
    content = template.render(Context(context))
    return dict(success=True, content=content)

@ajax
@login_required
def my_notifications_count(request):
    user = request.user
    count = user.get_profile().unread_notifications.count()
    return dict(success=True, count=count)

@ajax
@login_required
def user_notification_content(request, id):
    user = request.user
    notification = UserNotification.objects.get(id=id)
    if notification.user != user:
        return dict(success=False, message=_("You're not allowed to read a "
                                             "notification of another user."))
    if request.GET.get('read'):
        notification.mark_as_read()
    return dict(success=True, content=notification.message)

@login_required
def notification_template_test(request, id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    notification = Notification.objects.get(id=id)
    un = notification.users_notifications.all()[0]
    response = "<html><body><div>%s</div><hr/><div>%s</div></body></html>"
    return HttpResponse(response % (un.subject, un.email_message))
