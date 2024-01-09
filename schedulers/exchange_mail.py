# coding=utf-8
# 调用exchangelib 发送邮件
from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox, Body, Configuration, NTLM
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
# 此句用来消除ssl证书错误，exchange服务器使用自签证书需加上
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter


class ExchangeEmail:
    def __init__(self, username, password, server, primary_smtp_address):
        self.username = username
        self.password = password
        self.server = server
        self.primary_smtp_address = primary_smtp_address

    def send_email(self, to, subject, body):
        creds = Credentials(
            username=self.username,
            password=self.password
        )
        config = Configuration(
            server=self.server,
            auth_type=NTLM
        )
        account = Account(
            primary_smtp_address=self.primary_smtp_address,
            config=config,
            credentials=creds,
            autodiscover=True,
            access_type=DELEGATE
        )
        m = Message(
            account=account,
            subject=subject,
            body=Body(body),
            to_recipients=[Mailbox(email_address=to)]
        )
        m.send()
# 接收邮箱，主题，内容


if __name__ == '__main__':
    Email = ExchangeEmail('username', 'password', 'mail.ssecc.com.cn', 'xxxx@ssecc.com.cn')
    Email.send_email("xxxx@ssecc.com.cn", "abc", "def")
