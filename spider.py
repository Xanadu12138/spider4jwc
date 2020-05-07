from bs4 import BeautifulSoup
import requests
import hashlib
import config
import json
import re
import uuid
from datetime import date
from datetime import datetime
import time

#伪装用户
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}
session=requests.session()
#Login
def login(username_input,password_input):
    tologinurl='http://sso.jwc.whut.edu.cn/Certification/toLogin.do'
    tologin_response = session.get(tologinurl,headers=headers)
    soup=BeautifulSoup(tologin_response.content,'html.parser')
    hiddendata=soup.find_all('input',type='hidden')
    keylist=["type"]
    valuelist=["xs"]
    for data in hiddendata:
        if data.has_attr('value'):
            value=data.get('value')
        else:
            value=''
        key=data.get('name')
        keylist.append(key)
        valuelist.append(value)
    datadic=dict(zip(keylist,valuelist))
    webfinger=uuid.uuid4().hex
    datadic['webfinger'] = webfinger
    getcode = session.post('http://sso.jwc.whut.edu.cn/Certification/getCode.do',data={'webfinger':webfinger})
    datadic['code']=getcode.text
    #万事具备
    username=username_input
    password=password_input
    datadic['userName']=username
    datadic['password']=password
    if len(username) == 3:
        username="000" + username
    if len(username) == 4:
        username="00" + username
    if len(username) == 5:
        username="0" + username
    md5=hashlib.md5()
    sha=hashlib.sha1()
    usernameencode = username.encode(encoding='utf-8')
    md5.update(usernameencode)
    username1=md5.hexdigest()
    password0=username+password
    passwordencode=password0.encode(encoding='utf-8')
    sha.update(passwordencode)
    password1=sha.hexdigest()
    datadic['userName1']=username1
    datadic['password1']=password1
    login_response = session.post('http://sso.jwc.whut.edu.cn/Certification/login.do',data=datadic)
    return login_response
def analysize(content):
    ana_soup=BeautifulSoup(content,'html.parser')
    table=ana_soup.find('tbody',class_="table-class-even").children
    row_list=[]
    for row in table:
        cloumn_list=[]
        row_soup=BeautifulSoup(str(row),'html.parser')
        cloumns=row_soup.find_all('td',style="text-align: center")
        for cloumn in cloumns:
            cloumn_soup=BeautifulSoup(str(cloumn),'html.parser')
             #课程详细信息正则注册
            detail_reg=r'<div style=".*? color: .*?"><a href=".*?" style="color: .*?" target="_blank">(.*?)<p>(.*?)</p><p>.*\((.*?)-(.*?)节\)</p>'
            text=str(cloumn_soup).replace('\n','').replace('\t','').replace('\r','')
            detail=re.compile(detail_reg,re.S).findall(text)
            cloumn_list.append(detail)
        if cloumn_list:
            row_list.append(cloumn_list)
    time_period=['8:00','9:55','14:00','16:45','19:00']
    end_time_period=['8:45',"9:35","10:40","11:30","12:20","14:45","15:35","16:25","17:30","18:20","19:45","20:35","21:25"]
    week=["星期一","星期二","星期三","星期四","星期五","星期六","星期天"]
    dict_list=[]
    detail_dic_name=["Name","Site","Week","Start","End"]
    for time,curriculumns in zip(time_period,row_list):
        for curriculumn,day in zip(curriculumns,week):
            if len(curriculumn) > 0:     
                #print("课程:{0} 地点:{1} 星期:{2} 开始时间:{3} 结束时间:{4} {5}-{6}节".format(curriculumn[0][0],curriculumn[0][1],day,time,end_time_period[int(curriculumn[0][3])-1],curriculumn[0][2],curriculumn[0][3]))
                detail_list=[curriculumn[0][0],curriculumn[0][1],day,time,end_time_period[int(curriculumn[0][3])-1]]
                detail_dic=dict(zip(detail_dic_name,detail_list))
                if telltime(week.index(day),time):
                    dict_list.append(detail_dic)
    return_dic={'today':week[date.weekday(date.today())],'details':dict_list}
    return_json=json.dumps(return_dic,ensure_ascii=False)
    return return_json
    

def telltime(curriculumn_day, curriculumn_time):
    if int(curriculumn_day) < date.weekday(date.today()):
        return False
    elif datetime.strptime(curriculumn_time,'%H:%M') < datetime.strptime(str(datetime.now().hour)+":"+str(datetime.now().minute),'%H:%M') and curriculumn_day == date.weekday(date.today()):
        return False
    else:
        return True

def carwling(username_input,password_input):
    try:
        login_result = login(username_input,password_input)
        return_json=analysize(login_result.content)
        return return_json
    except Exception:
        return json.dumps({'msg':'用户名或密码不正确'},ensure_ascii=False)
    
if __name__ == "__main__":
    print(carwling(config.username,config.password))
   
    