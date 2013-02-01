from smtplib import SMTP
from email.mime.text import MIMEText

from django.conf import settings


def send_mail(subject, body, to, from_email=settings.NO_REPLY_EMAIL,
              html=False):
    to = settings.FAKE_EMAIL or to
    smtp = SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
    mtype = 'html' if html else 'plain'
    mimemsg = MIMEText(body, mtype, 'utf-8')
    mimemsg["Subject"] = subject
    mimemsg["From"] = from_email
    mimemsg["To"] = to
    smtp.sendmail(from_email, to, mimemsg.as_string())
    smtp.close()