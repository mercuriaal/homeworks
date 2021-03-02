import email
import smtplib
import imaplib

from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart


class Email:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def send_message(self, subject, text, *recipients):
        GMAIL_SMTP = "smtp.gmail.com"
        message = MIMEMultipart()
        message['From'] = self.login
        message['To'] = ', '.join(*recipients)
        message['Subject'] = subject
        message.attach(MIMEText(text))

        server = smtplib.SMTP(GMAIL_SMTP, 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.login, self.password)
        server.sendmail(self.login, server, message.as_string())
        server.quit()

    def receive_message(self, header=None):
        GMAIL_IMAP = "imap.gmail.com"
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP)
        mail.login(self.login, self.password)
        mail.list()
        mail.select('inbox')

        criteria = '(HEADER Subject "%s")' % header if header else 'ALL'
        result, data = mail.uid('search', None, criteria)
        assert data[0], 'There are no letters with current header'
        latest_email_uid = data[0].split()[-1]
        result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)

        mail.logout()


if __name__ == '__main__':
    user = Email('login@gmail.com', 'qwerty')
    user.send_message('Subject', 'Message', ['vasya@email.com', 'petya@email.com'])
    user.receive_message()
