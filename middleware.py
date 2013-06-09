import traceback

from django.conf import settings

from contact.mail import send_mail

class HeybaldockMiddleware(object):

    def process_exception(self, request, exception):
        """ All exception in site will be handled here and sent a report
            through email.
        """
        full = traceback.format_exc()
        subject = "Hey Baldock Site - Error Warning"
        body = "Exception: %s\n" % str(exception)
        body += "Logged user: %s\n" % request.user
        body += "Full Path: %s\n\n" % request.get_full_path()
        body += "Full traceback:\n\n%s" % full
        send_mail(subject, body, settings.MAIL_USER)
