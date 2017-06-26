# coding:utf-8
import smtplib
from email.mime.text import MIMEText

import configparser


class ZeusMail:
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("conf/zeus_config.conf")
        self.__user = cf.get('mail', 'user')
        self.__pwd = cf.get('mail', 'pwd')
        self.__to = cf.get('mail', 'to')

    def send_mail(self, calc_time, bp_data_frame, sp_data_frame):
        bp_count = len(bp_data_frame)
        text = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" //>'
        text += '<title>%s - bp:%d  sp:%d</title><//head>' % (calc_time.strftime('%Y-%m-%d %H:%M:%S'), bp_count, 0)
        text += '<p align = "center"> %s - bp:%d  sp:%d </p>' % (calc_time.strftime('%Y-%m-%d %H:%M:%S'), bp_count, 0)
        text += '<body><table border="1" align="center">'
        for index, row in bp_data_frame.iterrows():
            text += '<tr align="center" style="background:darkred"><td>买点</td>'
            text += '<td>%s</td><td>%s</td><td>%.3f</td></tr>' % (row['id_time'], row['code'], row['price'])
        for index, row in sp_data_frame.iterrows():
            text += '<tr align="center" style="background:darkred"><td>买点</td>'
            text += '<td>%s</td><td>%s</td><td>%.3f</td></tr>' % (row['id_time'], row['code'], row['price'])
        text += '</table></body></html>'

        msg = MIMEText(text, 'html', 'utf-8')
        msg["Subject"] = '%s - bp:%d  sp:%d' % (calc_time.strftime('%Y-%m-%d %H:%M:%S'), bp_count, 0)
        msg["From"] = self.__user
        msg["To"] = self.__to

        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(self.__user, self.__pwd)
            s.sendmail(self.__user, self.__to, msg.as_string())
            s.quit()
            print("Mail sending Success!")
        except smtplib.SMTPException as e:
            print("Mail sending Falied,%s" % e)
