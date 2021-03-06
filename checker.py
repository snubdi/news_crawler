# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
import scrapy
import MySQLdb
import smtplib
from email.mime.text import MIMEText
from prettytable import PrettyTable


#target medias
media_list = ['xinhua','163','naver','people','globaltimes','ce','yahoonews','sankei','yomiuri','asahi','nikkei','mainichi','cnn','msnbc','fox','lexisnexis']
#DB infomation
db_host = 'localhost'
db_name = 'internetNews'
db_user = 'mers_hwyun'
db_pw = 'buECAs5ePudeB92R'
#mailing infomation
mailto_list=["asan@bdi.snu.ac.kr"]
#mailto_list=["keith_wzh@hotmail.com"]
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
today = datetime.now() + timedelta(days = -0)
delay2 = datetime.now() + timedelta(days = -2)
delay3 = datetime.now() + timedelta(days = -3)
delay4 = datetime.now() + timedelta(days = -4)

check_date_today = today.strftime("%Y-%m-%d")
check_date_delay2 = delay2.strftime("%Y-%m-%d")
check_date_delay3 = delay3.strftime("%Y-%m-%d")
check_date_delay4 = delay4.strftime("%Y-%m-%d")

yesterday = datetime.now() + timedelta(days = -1)
today = datetime.now() + timedelta(days = -0)
check_date = yesterday.strftime("%Y-%m-%d")
check_date_today = today.strftime("%Y-%m-%d")

#For lexisnexis
last_one_week = (datetime.now() + timedelta(days = -7)).strftime("%Y-%m-%d")
last_two_week = (datetime.now() + timedelta(days = -14)).strftime("%Y-%m-%d")
sql_lexisnexis_last_one_week = u'select count(*) from articles_lexisnexis  where  date(date) >= "' + last_one_week + u'"'
sql_lexisnexis_last_two_week = u'select count(*) from articles_lexisnexis  where  date(date) >= "' + last_two_week + u'"'
cur.execute(sql_lexisnexis_last_one_week)
articleCountLexisnexis_last_one_week = cur.fetchone()[0]

cur.execute(sql_lexisnexis_last_two_week)
articleCountLexisnexis_last_two_week = cur.fetchone()[0]

#For each media in Naver
sql_naver_donga = u'select count(*) from articles_naver where date(date) = "' + check_date_today + u'"' + u'and agency = "동아일보"'
sql_naver_joongang = u'select count(*) from articles_naver where date(date) = "' + check_date_today + u'"' + u'and agency = "중앙일보"'
sql_naver_hani = u'select count(*) from articles_naver where date(date) = "' + check_date_today + u'"' + u'and agency = "한겨레"'
sql_naver_chosun = u'select count(*) from articles_naver where date(date) = "' + check_date_today + u'"' + u'and agency = "조선일보"'
sql_naver_khan = u'select count(*) from articles_naver where date(date) = "' + check_date_today + u'"' + u'and agency = "경향신문"'

cur.execute(sql_naver_donga)
articleCountNaver_donga = cur.fetchone()[0]

cur.execute(sql_naver_joongang)
articleCountNaver_joonang = cur.fetchone()[0]

cur.execute(sql_naver_hani)
articleCountNaver_hani = cur.fetchone()[0]

cur.execute(sql_naver_chosun)
articleCountNaver_chosun = cur.fetchone()[0]

cur.execute(sql_naver_khan)
articleCountNaver_khan = cur.fetchone()[0]


#check_date = yesterday.strftime("%Y-%m-%d")
info = "date: "+check_date + "\n"
info += '========================================\n'
#get count info from DB
info += '{0:15s} {1:12s} {2:12s}'.format('Media', 'ArticleCount', 'CommentCount') + "\n"
info += '----------------------------------------\n'
totalArticle, totalComment = 0,0
for media in media_list:
    sql = u'select count(*) from articles_'+media+' where  date(date) = "' + check_date + u'"'
    cur.execute(sql)
    articleCount = cur.fetchone()[0]
    totalArticle += articleCount
    if media == 'ce' :
        commentCount = 0
    elif media == 'sankei' :
        commentCount = 0
    elif media == 'yomiuri' :
        commentCount = 0
    elif media == 'asahi' :
        commentCount = 0
    elif media == 'nikkei' :
        commentCount = 0
    elif media == 'mainichi' :
        commentCount = 0
    elif media == 'cnn' :
        commentCount = 0
    elif media == 'msnbc' :
        commentCount = 0
    elif media == 'fox' :
        commentCount = 0
    elif media == 'lexisnexis' :
        commentCount = 0
    else:
        sql = u'select count(*) from comments_'+media+' where  date(date) = "' + check_date + u'"'
        cur.execute(sql)
        commentCount =cur.fetchone()[0]
    totalComment += commentCount
    info += '{0:15s} {1:12s} {2:12s}'.format(media,str(articleCount) ,str(commentCount)) + "\n"
    #insert to DB
    sql = u'replace into crawl_infomation values ("'+check_date+'","'+media+'",'+str(articleCount)+','+str(commentCount)+')'
    cur.execute(sql)
    conn.commit()

info += '----------------------------------------\n'
info += '{0:15s} {1:12s} {2:12s}'.format('Total', str(totalArticle), str(totalComment))
info += '\n----------------------------------------\n'
info += 'Naver_Dongai_today' + '        ' + str(articleCountNaver_donga) + '\n'
info += 'Naver_Joonang_today' + '      ' + str(articleCountNaver_joonang) + '\n'
info += 'Naver_Hani_today' + '         ' + str(articleCountNaver_hani) + '\n'
info += 'Naver_Chosun_today' + '       ' + str(articleCountNaver_chosun) + '\n'
info += 'Naver_Khan_today' + '         ' + str(articleCountNaver_khan) + '\n'
info += '----------------------------------------\n'
info += 'Lexisnexis_last 1 week' +'       ' + str(articleCountLexisnexis_last_one_week) + '\n'
info += 'Lexisnexis_last 2 week' +'       ' + str(articleCountLexisnexis_last_two_week)
#info += '{0:15s} {1:12s} {2:12s}'.format('Lexisnexis_lastweek', str(articleCountLexisnexis))
sql = u'replace into crawl_infomation values ("'+check_date+'","total",'+str(totalArticle)+','+str(totalComment)+')'
cur.execute(sql)
conn.commit()

print info

#send a email
me="BDIManager"+"<"+mail_user+"@"+mail_postfix+">"
msg = MIMEText(info,_subtype='plain',_charset='utf-8')
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
