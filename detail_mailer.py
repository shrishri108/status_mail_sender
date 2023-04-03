import smtplib
import pyodbc
from datetime import datetime,timedelta
import pandas as pd
import pandas.io.sql as sql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

server_url='' #enter your db url
username=''
password=''
cnxn = pyodbc.connect('Driver={SQL Server};SERVER={};DATABASE=brand_name;UID={};PWD={}'.format(server_url,username,password))
cursor = cnxn.cursor()

todays = datetime.now()
time_stamp = todays.strftime("%Y-%m-%d")
time_stamp2 = todays.strftime("%Y-%m-%d")
#print(time_stamp2)

SUBJECT = "Brand : " + time_stamp + " Status Report "

df_osa = pd.read_sql_query("SELECT * FROM brand_name_item_view_product_info",cnxn)

master = pd.read_excel('mailer_master.xlsx','Sheet1') #get product_info excel template, need to have an offline excel template for multiple platform and multiple values

df_osa.to_html("brand_name_osa_mail.html",index=False) #df to html

merged = pd.merge(master,df_osa, how='left',left_index=False, right_index=False, sort=True,left_on=None, right_on=None)
df = pd.DataFrame(merged)

df_new = df[["Date","Platform","Location Count","Expected Location","Total SKU Count"]]
df_new['Expected SKU Count'] = df['Expected SKUs'] * df['Expected Location']
df_new["Status Blanks"] = df["Status Blanks"]
df_new["Price Blanks"] = df["Price Blanks"]
check =[]
for index,row in df.iterrows():
    if (row['Expected SKUs'] * row['Expected Location'] != row['Total SKU Count'] or row['Expected Location'] != row['Location Count'] or row['Status Blanks'] > 0 or row['Price Blanks']):
        check.append('Alert!')
    else:
        check.append('')
df_new['Check'] = check

df.to_html('brand_name_osa_mail.html',index=False)

html_file = open('brand_name_osa_mail.html')
message1 = html_file.read()
        
heading1='<h3>brand_name OSA Summary:  '+ time_stamp + '</h3></br>'

# Detailed BSR, Brand Health and Visibility table
df_final = pd.read_sql_query("SELECT * FROM brand_name_mailer",cnxn) #brand_name_mailer being the 'view' in database

df_final.to_html("brand_name_rest_mail.html",index=False)
heading2='<h3>brand_name Detailed Summary:  '+ time_stamp + '</h3></br>'
html_file = open('brand_name_rest_mail.html')
message2 = html_file.read()
brandhealth=pd.read_sql_query('''select time_stamp,pname,platform_code,platform,cust_rating from brand_name_brand_rating where time_stamp=(?) and cust_rating is NULL''',cnxn,params=(time_stamp,))
brandhealth.to_html('brandhealth.html')
bh=open('brandhealth.html')
bh=bh.read()

styling='<style >table {text-align: center;width: 75%;}th {background-color: #04aa6d;color: white;text-align: center;} h5 {color: red;text-align: left;}</style >'

ending='<h5>*In case of any discrepancy please contact @Person Name</h5></br> width="150" height="50">'

heading_brandhealth='<h3>brand_name BrandHealth Blanks:  '+ time_stamp + '</h3></br>'
comp_html="<html><head>"+styling+"<body></body>"+heading1+message1+"<br>"+heading2+message2+heading_brandhealth+bh+ending+"</head></html>"


#Mailer 
s = smtplib.SMTP('smtp-mail.outlook.com', 587)
s.ehlo()
s.starttls()
email='' #sender's email
password='' #sender's password to login to SMTP
s.login("{}".format(email), "{}".format(password))

#Sender and Reciver mails
email_user = "" #sender's email address
email_send = [''] #list of email addressess to send mail to

msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = (', ').join(email_send)
msg['Subject'] = SUBJECT

# message to be sent
msg = MIMEMultipart()
msg['Subject'] = SUBJECT
HTML_BODY = MIMEText(comp_html, 'html')
msg.attach(HTML_BODY)

text = msg.as_string()

try:
    s.sendmail(email_user,email_send,text)
    print ('email sent')
except:
    print ('error sending mail')

