import smtplib
import getpass
import sys

from email.mime.text import MIMEText

class MailClient(object):

    def __init__(self, login_name, smtp_host, smtp_port=465):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.login_name = login_name
        self.login_pwd = ""

        try:
            self.conn = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            print("Connect to mail server '{0}:{1}' successfully.".format(self.smtp_host, self.smtp_port))
        except:
            print("Unable to connect to mail server '{0}:{1}' !!".format(self.smtp_host, self.smtp_port))
            self.conn = None
    
    def reconnect(self):
        try:
            self.conn = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            print("Connect to mail server '{0}:{1}' successfully.".format(self.smtp_host, self.smtp_port))
            return True
        except:
            print("Unable to connect to mail server '{0}:{1}' !!".format(self.smtp_host, self.smtp_port))
            self.conn = None
            return False

    def isConnectionFailed(self):
        return self.conn == None

    def login(self):
        try:
            self.login_pwd = getpass.getpass("Please enter login password for mail server: ")
            self.conn.login(self.login_name, self.login_pwd)
            print("Login mail server successfully.")
            return True
        except:
            print("Unable to login !!")
            return False


    def login_auto(self):
        if self.login_pwd == "":
            print("No password!!  Unable to login !!")
            return False
        try:
            self.conn.login(self.login_name, self.login_pwd)
            print("Login mail server successfully.")
            return True
        except:
            print("Unable to login !!")
            return False


    def sendmail(self, msg):
        try:
            self.conn.sendmail(msg['From'], [ msg['To'] ], msg.as_string())
            print("Sent mail successfully.")
            return True
        except:
            print("Unable to send mail !!")
            return False

    def quit(self):
        self.conn.quit()
        print("Disconnect to mail server.")
    

if __name__ == '__main__':

    mc = MailClient('aaaaaa@bbbbb.com', 'smtp.bbbbb.com')
    if mc.isConnectionFailed():
        sys.exit(None)

    msg = MIMEText('This is mail message.')
    msg['Subject'] = 'This is mail title'
    msg['From'] = 'aaaaaa@bbbbb.com'
    msg['To'] = 'cccccc@bbbbb.com'

    if not mc.login():
        sys.exit(None)
    mc.sendmail(msg)
    mc.quit()
