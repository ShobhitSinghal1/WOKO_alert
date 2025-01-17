from urllib.request import urlopen
import ssl
import smtplib
import time
import random
from bs4 import BeautifulSoup
import yaml
from twilio.rest import Client

with open("config.yaml", "r") as opened_file:
    config = yaml.safe_load(opened_file)


def call(**kwargs):
    """

    :param kwargs:
    :return:
    """
    account_sid = config["account_sid"]
    auth_token = config["auth_token"]
    from_number = config["from_number"]
    to_number = config["to_number"]
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        twiml='<Response><Say>New room, check website</Say></Response>',
        to=to_number,
        from_=from_number
    )

def send_message(**kwargs):
    """
    Send email if the number of rooms on WOKO is changed
    :param content:
    :param receiver_email:
    :param sender_email:
    :param password:
    :return:
    """
    content = kwargs.get('content')
    receiver_email = kwargs.get('receiver_email')
    sender_email = kwargs.get('sender_email')
    password = kwargs.get('password')

    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    message = f"Subject: You have a new post\n\n\n{content}.\n\n\nCheers,\nYour team"
    print(message)
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    print('Message send!')

def query_all_website():
    """
    Check the WOKO website for the number of available rooms
    :return: Number of rooms
    """
    url = config["url_woko"]
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = [chunk for chunk in chunks if config["keyword"] in chunk]
    return text

def sleep():
    """
    Sleep time
    :return:
    """
    timer = config["timer"] * random.choice([1, 2])
    print(f"Sleep for: {timer // 60}min.")
    time.sleep(timer)


memory_list = query_all_website()

while True:
    try:
        new_memory_list = query_all_website()

        if len(memory_list) < len(new_memory_list) or config['test']:
            # send_message(**config)
            call(**config)
            print("Found!")
            memory_list = new_memory_list
            sleep()
        else:
            print(f"Still: {len(new_memory_list)} rooms...")
            memory_list = new_memory_list
            sleep()
    except Exception as e:
        print(f'{e}')
