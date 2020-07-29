import os
import smtplib
import ssl
from socket import gaierror
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from threading import Thread

from services.smtp.email_templates import load_signup_template, load_notification_template

smtp_pass = os.environ.get('SMTP_PASS')
sender = "Daftar Notifications <daftar.sih2020@gmail.com>"

# Dafar Logo
fp = open('images/logo.png', 'rb')
image = MIMEImage(fp.read())
image.add_header('Content-ID', '<DaftarLogo>')
fp.close()

# Create a secure SSL context
context = ssl.create_default_context()


def send_email_async(receiver, type, username=None, notif=None, pin=None):
    thread = Thread(target=send_email, args=(receiver, type, username, notif, pin))
    thread.start()


def send_email(receiver, type, username=None, notif=None, pin=None):
    message = make_message(receiver, type, username=username, notif=notif, pin=pin)
    try:
        if not smtp_pass:
            # Use MailTrap Testing Server
            with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
                server.login("d9d28fda0b14dd", "4276a54ec00cb6")
                server.sendmail(sender, receiver, message.as_string())
        else:
            # Use Official Mailing Server
            # TODO
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login("daftar.sih2020@gmail.com", smtp_pass)
                server.sendmail(sender, receiver, message.as_string())

        print('Message Sent')
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the server. Bad connection settings?')
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
        print('smtp error occurred: ' + str(e))


def make_message(receiver, type, notif, username=None, pin=None):
    message = MIMEMultipart("alternative")
    message["From"] = sender
    if username is not None:
        message["To"] = f"{username} <{receiver}>"
    else:
        message["To"] = receiver

    if type == 'signup':
        message["Subject"] = "Welcome to E-Daftar! Verify Email"
        build_signup_mail(message, username, pin)
    elif type == 'notification':
        message["Subject"] = "Daftar Notifications!"
        build_notification_mail(message, username, notif)

    return message


def build_signup_mail(message, username, pin):

    text = f"""\
Thanks for Signing Up!
Welcome to E-Dafar, {username}. Please click on the below button to verify your account.
http://daftar-webapp.herokuapp.com/verify={pin}
!"""

    html = load_signup_template().format(username=username, pin=pin)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    message.attach(image)


def build_notification_mail(message, username, content):
    text = f"""\
You have a new Notification!
{content}
!"""

    html = load_notification_template().format(username=username, content=content)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    message.attach(image)


# Test Example
#send_email('manjot.gni@gmail.com', 'notification', username='Manjot', notif='Your Application is signed by Admin!. Please check E-Daftar portal for more.')
