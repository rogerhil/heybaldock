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
    msgfrom = _("Message from %s, e-mail: %s\n\n" % (name, fromemail))
    mimemsg = MIMEText(msgfrom + msg, 'plain', 'utf-8')
    mimemsg["Subject"] = subject
    mimemsg["From"] = fromemail
    mimemsg["To"] = settings.MAIL_USER
    smtp.sendmail(fromemail, settings.MAIL_USER, mimemsg.as_string())
    smtp.close()