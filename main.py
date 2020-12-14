from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime as dt

def getweathernews():
    #USING THE HEADLESS MODE OF CHROME WEBDRIVER TO GET TO SEARCH PAGE
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    #SEARCHING FOR THE RESPECTIVE CITY WEATHER
    city = "Mumbai"
    driver.get("http://www.google.com")
    search = driver.find_element_by_name("q")
    search.send_keys(city+" weather")
    search.send_keys(Keys.RETURN)

    tempC_text = driver.find_element_by_id("wob_tm")
    tempC = int(tempC_text.text)
    tempF = int(((9*tempC)/5)+32)

    precipitation_text = driver.find_element_by_id("wob_pp")
    precipitation = precipitation_text.text
    humidity_text = driver.find_element_by_id("wob_hm")
    humidity = humidity_text.text
    windK_text = driver.find_element_by_id("wob_ws")
    windK = windK_text.text

    f = open("message.txt", 'w')
    f.write("GOOD MORNING ${PERSON_NAME}\n")
    f.write("THE WEATHER OF ${CITY_NAME} IS AS FOLLOWS:\n")
    f.write("TEMPERATURE IN CELSIUS: "+str(tempC)+"C\n")
    f.write("TEMPERATURE IN FAHRENHEIT: "+str(tempF)+"F\n")
    f.write("PRECIPITATION: "+precipitation+"\n")
    f.write("HUMIDITY: "+humidity+"\n")
    f.write("WIND: "+windK+"\n\n")

    #SEARCHING FOR WORLD NEWS
    f.write("WORLD NEWS FOR TODAY:")
    source = requests.get("https://www.bbc.com/news/world").text
    soup = BeautifulSoup(source, 'lxml')

    news = soup.find('div', class_='gs-c-promo-body gs-u-mt@xxs gs-u-mt@m gs-c-promo-body--primary gs-u-mt@xs gs-u-mt@s gs-u-mt@m gs-u-mt@xl gel-1/3@m gel-1/2@xl')
    top_news = news.h3.text
    f.write("\n")
    f.write(top_news+"\n")
    summary = news.p.text
    f.write("    "+summary+"\n")


    for article in soup.find_all('div', class_='gs-c-promo-body gs-u-mt@xxs gs-u-mt@m gs-c-promo-body--flex gs-u-mt@xs gs-u-mt0@xs gs-u-mt--@s gs-u-mt--@m gel-1/2@xs gel-1/1@s'):
        header = article.h3.text
        f.write("\n"+header+"\n")
        summary = article.p.text
        f.write("    " + summary + "\n")

    f.write("\nWANT TO READ MORE. CLICK HERE --------->  https://www.bbc.com/news/world")
    f.close()

def send_email():
    #setting up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login("pyaut2710@gmail.com", "python@123")


    def get_contacts(filename):
        names = list()
        emails = list()
        cities = list()
        with open(filename,'r') as contacts_file:
            for a_contact in contacts_file:
                names.append(a_contact.split()[0])
                emails.append(a_contact.split()[1])
                cities.append(a_contact.split()[2])
            return names,emails,cities


    def read_template(filename):
        with open(filename,'r') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    names,emails,cities = get_contacts('mycontacts.txt')
    message_template = read_template('message.txt')


    for name,email,city in zip(names,emails,cities):
        msg = MIMEMultipart()
        message = message_template.substitute(PERSON_NAME = name.title(), CITY_NAME = city.title())
        msg ['FROM'] = 'Shireen'
        msg['TO'] = email
        msg['SUBJECT'] = 'THE DAYPY'

        msg.attach(MIMEText(message, 'plain'))

        s.send_message(msg)

        del msg

    s.quit()

def send_email_at(send_time):
    time.sleep(send_time.timestamp() - time.time())
    getweathernews()
    send_email()
    print('email sent')

getweathernews()
first_email_time = dt.datetime(2020,12,15,8,0,0) # set your sending time in UTC
interval = dt.timedelta(hours=24) # set the interval for sending the email

send_time = first_email_time
while True:
    send_email_at(send_time)
    send_time = send_time + interval
