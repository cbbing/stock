# -*- coding: utf8 -*-

__author__ = 'Cbb'
from init import *

def send_email_163(from_addr= 'cbbhust@163.com',
                   password = '12356789',
                   to_addrs = ('m18410182275@163.com'),
                   subject= 'Result',
                   content = None):
    """This function use 163 email to send simple message.If success,return Ture,else return False
    from_addr:should be 163 email adress
    password:password of your email account
    to_addrs:should be a tuple,like ('xxxxxx@163.com','xxxxxx@163.com')
    subject:subject of your email
    content:content of your email
    """
    if content == None:
        errorLogger.logger.error( 'content is None.')
        return False

    try:
        from smtplib import SMTP
        from email.mime.text import MIMEText

        infoLogger.logger.info('begin send email...')

        email_client = SMTP(host = 'smtp.163.com')
        email_client.login(from_addr, password)

        #create msg
        msg = MIMEText(content, _charset='utf-8')
        msg['Subject'] = subject
        email_client.sendmail(from_addr, to_addrs, msg.as_string())

        infoLogger.logger.info('send email success!')
        return True

    except Exception, e:
        errorLogger.logger.error(str(e))
        return False
    finally:
        email_client.quit()

if __name__ == '__main__':
    send_email_163(content='tttt')



