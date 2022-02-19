#!/usr/bin/env python3


import unittest
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from .email_hook import EmailHook


class TestEmail(unittest.TestCase):
    def test_email(self):
        host = "smtp.qq.com"
        port = 465
        username = "hatlonely@foxmail.com"
        password = "******"
        receiver = "hatlonely@foxmail.com"
        subject = "Test 测试报告"
        body = "<p>hello world</p>"

        message = MIMEText(body, 'html', 'utf-8')
        message['From'] = Header(username, 'utf-8')
        message['To'] = Header(receiver, 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        smtp = smtplib.SMTP_SSL(host, port)
        smtp.login(username, password)
        smtp.sendmail(username, receiver.split(";"), message.as_string())
        print("邮件发送成功")


class TestEmailHook(unittest.TestCase):
    def test_email(self):
        hook = EmailHook({
            "endpoint": "smtp.qq.com:465",
            "username": "hatlonely@foxmail.com",
            "password": "******",
            "receiver": "hatlonely@foxmail.com",
        })


def main():
    unittest.main()


if __name__ == "__main__":
    main()
