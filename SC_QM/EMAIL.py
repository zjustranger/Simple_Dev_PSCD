import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import requests
import urllib.parse


class Email:
    '''
    此通用类用于发送邮件，有三个必填参数。格式范例如下:
    title: '来自Python的邮件轰炸测试……' (Mandatory)
    content: 'Hello! Send by Chauncey to test automail with Attachments' (Mandatory)
    receivers: 'chixiao.yang@polestar.com; zhongwei.he@polestar.com' (Mandatory)
    attachments: r'C:\temp\Warehouse_structure.xlsx' default None  (Optional)
    attachment_show_name: '1.xlsx' default 'attachment'  (Optional, mandatory if the above parameter is given)
    '''
    def __init__(self, title, content, receivers=None, attachments=None, attachment_show_name='attachment'):
        self.title = title
        self.content = content
        self.receivers = receivers
        self.attachments = attachments
        self.attachment_show_name = attachment_show_name
    def send_mail(self, sender_name_show='pscdrpt1.chn@volvocars.com'):
        from_addr = 'pscdrpt1.chn@volvocars.com'
        # password = 'Polestar@2020'
        to_addr = self.receivers
        smtp_server = 'mailrelay.volvocars.net'
        # smtp_server = 'smtp.office365.com'

        # 创建邮件对象, 根据有没有附件，新建MIMEMultipart对象或者MIMENonMultipart对象
        if self.attachments:
            msg = MIMEMultipart()
            msg['From'] = sender_name_show
            msg['To'] = to_addr
            msg['Subject'] = Header(self.title, 'utf-8').encode()

            # 添加邮件正文
            msg.attach(MIMEText(self.content, 'plain', 'utf-8'))

            # 添加附件
            if self.attachments:
                excelFile = self.attachments
                excelPart = MIMEApplication(open(excelFile, 'rb').read())
                excelPart.add_header('content-disposition', 'attachment', filename=self.attachment_show_name)
                msg.attach(excelPart)
        else:
            msg = MIMEText(self.content, 'plain', 'utf-8')
            msg['From'] = sender_name_show
            msg['To'] = to_addr
            msg['Subject'] = Header(self.title, 'utf-8').encode()


        # 发送邮件
        server = smtplib.SMTP(smtp_server, 25)
        server.set_debuglevel(1)
        # server.ehlo()
        # server.starttls()
        # server.ehlo()
        # server.login(from_addr, password)
        server.sendmail(from_addr, to_addr.split(';'), msg.as_string())
        server.quit()

class WeChatPusher:
    '''
        此通用类用于往自己的微信接口测试号上实时推送消息，有两个必填参数。格式范例如下:
        title: '微信推送标题' (Mandatory)
        content: '微信推送内容，支持Markdown语法' (Mandatory)
        usingvolvoproxy: '布尔值，默认True，从内网发起http request需要走代理' (Optional)
    '''
    def __init__(self, title, content, usingvolvoproxy = True):
        self.url_common = 'https://sctapi.ftqq.com/SCT546TUleK318ftXxwbmXw57aQBIc3.send?title={}&desp={}'
        self.proxies = {'http': '10.240.2.200:83', 'https': '10.240.2.200:83'}
        self.title = title
        self.content = content
        self.usingvolvoproxy = usingvolvoproxy
        self.url = self.url_common.format(urllib.parse.quote(self.title), urllib.parse.quote(self.content))
    def send(self):
        if self.usingvolvoproxy:
            self.r = requests.post(self.url, proxies=self.proxies)
        else:
            self.r = requests.post(self.url)





if __name__ == '__main__':
    # email = Email('来自Python的邮件轰炸测试……', 'Hello! Send by Chauncey to test automail with Attachments', 'chixiao.yang@polestar.com', r'C:\temp\Warehouse_structure.xlsx', 'wh.xlsx')
    # email = Email('测试：邮件发送自内网服务器', '此邮件通过内网连接mailrelay服务器'+'\n\n\n*** This e-mail was automatically generated and replies will not be read. ***', 'chixiao.yang@polestar.com')
    # email.send_mail('MAILAPI_PSCD')
    # print(WeChatPusher.__doc__)
    wechat = WeChatPusher('测试微信推送类', '''小伙砸，该喝水啦！''')
    wechat.send()