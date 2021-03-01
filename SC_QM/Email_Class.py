import os
import time
import socks
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from string import Template


class Logs:
    """
    日志格式化数据工具类
    """

    def __init__(self):
        self.fmt = '%Y-%m-%d %H:%M:%S'

    def __call__(self, log_type, msg):
        """
            日志格式化输出
            :param log_type: INFO ERROR WARN
            :param msg: MSG TEXT
            :return: None
        """

        date_detail = time.strftime(self.fmt)
        log_text = '[%s] %s' % (date_detail, msg)
        if log_type == 'INFO':
            print
            '\033[32;1m[INFO ] %s\033[0m' % log_text
        elif log_type == 'ERROR':
            print
            '\033[31;1m[ERROR] %s\033[0m' % log_text
        elif log_type == 'WARN':
            print
            '\033[33;1m[WARN ] %s\033[0m' % log_text


class Mail:
    """
    邮件发送工具类
    """

    def __init__(self, mail_host, mail_user, mail_pass, proxy=False):
        """
        初始化邮箱设置
        :param mail_host: string 邮箱服务器地址
        :param mail_user: string 发件人
        :param mail_pass: string 密码
        :param proxy: boolean
        """
        try:
            log('INFO', '初始化邮箱....')
            if proxy:
                log('INFO', '使用代理发送....')
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '10.240.2.200', 83)
                socks.wrapmodule(smtplib)
            self.me = '<' + mail_user + '>'
            self.server = smtplib.SMTP()
            self.server.connect(mail_host)
            self.server.login(mail_user, mail_pass)
        except Exception as e:
            log('ERROR', '[Mail->__init__] --> errmsg:%s' % (str(e)))

    def __call__(self, to_list, sub, body, images):
        """
        邮件发送
        :param to_list: list 收件人列表
        :param sub:  string 主题
        :param body:  string 正文
        :param images:  dict 图片
        :return:  None
        """

        def add_img(src, img_id):
            """
            邮件正文添加图片
            :param src: string 图片路径
            :param img_id: string 图片id
            :return: MIMEImage
            """
            try:
                fp = open(src, 'rb')
                msg_image = MIMEImage(fp.read())
                fp.close()
                msg_image.add_header('Content-ID', img_id)
                return msg_image
            except Exception as ex:
                log('ERROR', '[Mail->__call__->add_img] --> errmsg:%s' % (str(ex)))

        msg = MIMEMultipart('related')
        msg_text = MIMEText(body, 'html', 'utf-8')
        msg.attach(msg_text)
        if images:
            for k, v in images.iteritems():
                msg.attach(add_img(k, v))

        msg['Subject'] = sub
        msg['From'] = self.me
        msg['To'] = ','.join(to_list)
        try:
            log('INFO', '开始发送邮件....')
            self.server.sendmail(self.me, to_list, msg.as_string())
            log('INFO', '邮件发送成功....')
        except Exception as e:
            log('ERROR', '[send_mail] --> errmsg:%s' % (str(e)))

    def __del__(self):
        self.server.close()


log = Logs()
