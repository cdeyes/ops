# -*- coding: utf-8 -*-
import getopt
import sys
import smtplib
import re
import os
import logging
import email.MIMEMultipart # import MIMEMultipart
import email.MIMEText  # import MIMEText
from email.mime.application import MIMEApplication
logfile='/var/log/sendmail.log'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                    filename=logfile)



def smail(toaddrs,mail_body,subject,attachments=[]):
    #print toaddrs,mail_body,subject,attachments
    server = smtplib.SMTP('smtp.xxx.net')
    server.login('xxxx','xxxx')
    fromaddr = 'xxx@xxx.com'
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(mail_body,_charset="utf-8")
    main_msg.attach(text_msg)
    if attachments:
         for attachment in attachments:
             try:
                 with open(attachment,'rb') as af:
                    file_msg=MIMEApplication(af.read())
                    basename = os.path.basename(attachment)
                    file_msg.add_header('Content-Disposition','attachment', filename = basename)
                    main_msg.attach(file_msg)
             except IOError,e:
                    ermsg=e.strerror+':'+e.filename+' '+toaddrs
                    logging.error(ermsg)
    main_msg['From'] = fromaddr
    main_msg['To'] = ','.join(toaddrs)
    main_msg['Subject'] = subject
    main_msg['Date'] = email.Utils.formatdate()
    fullText = main_msg.as_string()

    try:
        #server.set_debuglevel(1)
        server.sendmail(fromaddr, toaddrs, fullText)
    except:
        return 1
    server.quit()
    return 0



if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:a:")
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)
    output = None
    subject = ""
    toaddrs = ""
    mail_body = ""
    attachment = ""
    for o, a in opts:
        if o == "-s":
            subject = a
        elif o in ("-h"):
            print "echo message|%s -s subject -t mailaddr -a 'a.file,b.file' " %(sys.argv[0])
            sys.exit()
        elif o in ("-a"):
            s = re.compile(r"([^,]+)")
            attachment = s.findall(a)
        elif o in ("-t"):
            #s = re.compile(r"([^,]+)")
            #toaddrs = s.findall(a)
            toaddrs = a.split(',')
    while(1):
        try:
            tmp=raw_input()
        except EOFError:
            break
        mail_body = '%s\n%s' % (mail_body,tmp)

    smail(toaddrs, mail_body,subject,attachment)