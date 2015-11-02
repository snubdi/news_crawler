# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
import scrapy
import MySQLdb
import smtplib  
from email.mime.text import MIMEText  
from prettytable import PrettyTable

#target medias
media_list = ['xinhua','163','naver','people','globaltimes']
#DB infomation
db_host = 'localhost'
db_name = 'internetNews'
db_user = 'mers_hwyun'
db_pw = 'buECAs5ePudeB92R'
#mailing infomation
mailto_list=["yunhiwen@hotmail.com","keith_wzh@hotmail.com","cuism1987@hotmail.com",] 
mail_host="smtp.gmail.com"
mail_user="bigdata2015.snu"
mail_pass="bigdata2015" 
mail_postfix="gmail.com"  

#DB connection
try:
    conn = MySQLdb.connect(
            host = db_host,
            user = db_user,
            passwd = db_pw,
            charset = 'utf8')
    cur = conn.cursor()
    conn.select_db(db_name)
except MySQLdb.Error, e:
    print 'MySQL error %d: %s' % (e.args[0], e.args[1])
yesterday = datetime.now() + timedelta(days = -1)
check_date = yesterday.strftime("%Y-%m-%d")
info = "date: "+check_date + "\n"

#get count info from DB
pt = PrettyTable(field_names=['Media', 'articleCount', 'CommentCount'])
for media in media_list:
    sql = u'select count(*) from articles_'+media+' where  date(date) = "' + check_date + u'"'
    cur.execute(sql)
    articleCount = str(cur.fetchone()[0])
    sql = u'select count(*) from comments_'+media+' where  date(date) = "' + check_date + u'"'
    cur.execute(sql)
    pt.add_row([media,articleCount,str(cur.fetchone()[0])])

print info + pt.get_string()

#send a email
me="BDIManager"+"<"+mail_user+"@"+mail_postfix+">"  
msg = MIMEText(info + pt.get_string(),_subtype='plain',_charset='utf-8')  
msg['Subject'] = "Crawler daily report " + check_date
msg['From'] = me  
msg['To'] = ";".join(mailto_list)  
try:  
    server = smtplib.SMTP(mail_host)
    server.ehlo()
    server.starttls()
    server.login(mail_user,mail_pass)  
    server.sendmail(me, mailto_list, msg.as_string())  
    server.close()   
except Exception, e:  
    print str(e)  