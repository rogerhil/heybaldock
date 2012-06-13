from smtplib import SMTP
from email.mime.text import MIMEText

from django.conf import settings
from django.utils.translation import ugettext as _

def send_mail(name, fromemail, subject, msg):
    smtp = SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
    subject = _("Message from website: %s" % subject)
    args = dict(name=name, email=fromemail)
    msgfrom = _("Message from %(name)s, e-mail: %(email)s\n\n" % args)
    mimemsg = MIMEText(msgfrom + msg, 'plain', 'utf-8')
    mimemsg["Subject"] = subject
    mimemsg["From"] = fromemail
    mimemsg["To"] = settings.MAIL_USER
    smtp.sendmail(fromemail, settings.MAIL_USER, mimemsg.as_string())
    smtp.close()