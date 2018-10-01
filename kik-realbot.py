"""
A Kik bot that just logs every event that it gets (new message, message read, etc.),
and echos back whatever chat messages it receives.
"""

import kik_unofficial.datatypes.xmpp.chatting as chatting
from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.datatypes.xmpp.errors import SignUpError, LoginError, NetworkError
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse, PeerInfoResponse
from kik_unofficial.datatypes.xmpp.sign_up import RegisterResponse, UsernameUniquenessResponse
from kik_unofficial.datatypes.xmpp.login import LoginResponse, ConnectionFailedResponse
import time
import datetime
import sys
from multiprocessing import Process
from threading import Thread
import threading

username = 'rosa90i'
password = 'asdqwe123'

template_path = "templates.txt"
delay_path = "delays.txt"
message_templates = []
message_delays = []
delay_times = 0
i = 0
# last_reqtime = datetime.datetime.now()
# sent_time = datetime.datetime.now()
# lock = False

def Read_templates():
    count = 0
    with open(template_path, encoding='utf8') as fp:
        line = fp.readline()
        if line.strip() != '':
            message_templates.append(line.strip())
            count = count + 1
        while line:
            line = fp.readline()
            if line.strip() != '':
                message_templates.append(line.strip())
                count = count + 1
    print(count, "messages read\n")
    return

def Read_delays():
    count = 0
    with open(delay_path, encoding='utf8') as fp:
        line = fp.readline()
        if line.strip() != '':
            message_delays.append(int(line.strip()))
            count = count + 1
        while line:
            line = fp.readline()
            if line.strip() != '':
                message_delays.append(int(line.strip()))
                count = count + 1
    print(count, "delays read\n")
    return

class user():
    def __init__(self):
        self.lock = False
        self.last_reqtime = datetime.datetime.now()
        self.sent_time = datetime.datetime.now()
        self.body = ''
        self.count = 0
    def set_fromid(self, id):
        self.fromid = id

def main():
    bot = EchoBot()

class EchoBot(KikClientCallback):
    def __init__(self):
        self.users = {}
        self.offset = []
        self.lock = False
        self.interval = 120
        self.client = KikClient(self, username, password, kik_node="rosa90i_bwp")
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        time.sleep(self.interval)
        #self.client.loop.stop()
        while True:
            print('Send Test Message')
            self.client.send_chat_message("animal2231123_lnd@talk.kik.com","Test Message")
            time.sleep(self.interval)

    def on_authenticated(self):
        print("Now I'm Authenticated, let's request roster")
        self.client.request_roster()

    def on_login_ended(self, response: LoginResponse):
        print("Full name: {} {}".format(response.first_name, response.last_name))

    def send_message(self, fromid):
        # if self.offset[str(self.chatmessage.from_jid)] + 1 > len(message_templates):
        #     return
        print(fromid)
        print("start")
        time.sleep(2)
        now = datetime.datetime.now()
        while (now - self.users[fromid].last_reqtime).total_seconds() < 2:
            print("delaytime:", (self.users[fromid].last_reqtime - now).total_seconds() + 2)
            time.sleep((self.users[fromid].last_reqtime - now).total_seconds() + 2)
            now = datetime.datetime.now()
        incoming_file = open("Incoming.txt", "a+")
        now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        incoming_file.write(now + " " + fromid + "->" + self.users[fromid].body + "\n")
        print("SEND")
        self.client.send_is_typing(fromid, True)
        time.sleep(2)
        #count = self.offset[str(self.chatmessage.from_jid)]
        count = self.users[fromid].count
        try :
            time.sleep(message_delays[count])
        except :
            a = 0
        message_type = message_templates[count].split("|")[0]
        message_body = message_templates[count].split("|")[1]
        if message_type == "text":
            self.client.send_chat_message(fromid, message_body)
        if message_type == "picture":
            a = 1
            # self.client.send_image_message(chat_message.from_jid, message_body)

        #self.offset[str(self.chatmessage.from_jid)] = count + 1
        self.users[fromid].count = count + 1

        incoming_file.close()

        self.users[fromid].lock = False
        self.client.send_is_typing(fromid, False)
        print("end")
    def on_chat_message_received(self, chat_message: chatting.IncomingChatMessage):
        if str(chat_message.from_jid) not in self.users:
            tuser = user()
            tuser.set_fromid(str(chat_message.from_jid))
            self.users[str(chat_message.from_jid)] = tuser
        incoming_file = open("Incoming.txt", "a+")
        self.users[str(chat_message.from_jid)].last_reqtime = datetime.datetime.now()
        print("last_reqtime",self.users[str(chat_message.from_jid)].last_reqtime)
        print("lock",self.users[str(chat_message.from_jid)].lock)
        if self.users[str(chat_message.from_jid)].lock == False:
            self.users[str(chat_message.from_jid)].lock = True
            print("lock",self.users[str(chat_message.from_jid)].lock)
        else:
            now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            incoming_file.write(now + " " + chat_message.from_jid + "->" + chat_message.body + "\n")
            print("skip")
            return
        #self.chatmessage = chat_message
        self.users[str(chat_message.from_jid)].body = chat_message.body
        thread = Thread(target = self.send_message, args=(chat_message.from_jid,))
        thread.start()

        # thread = Thread(target = self.temp_thread())
        # thread.start()

    def on_message_delivered(self, response: chatting.IncomingMessageDeliveredEvent):
        print("[+] Chat message with ID {} is delivered.".format(response.message_id))

    def on_message_read(self, response: chatting.IncomingMessageReadEvent):
        print("[+] Human has read the message with ID {}.".format(response.message_id))

    def on_group_message_received(self, chat_message: chatting.IncomingGroupChatMessage):
        print("[+] '{}' from group ID {} says: {}".format(chat_message.from_jid, chat_message.group_jid,
                                                          chat_message.body))

    def on_is_typing_event_received(self, response: chatting.IncomingIsTypingEvent):
        print("[+] {} is now {}typing.".format(response.from_jid, "not " if not response.is_typing else ""))

    def on_group_is_typing_event_received(self, response: chatting.IncomingGroupIsTypingEvent):
        print("[+] {} is now {}typing in group {}".format(response.from_jid, "not " if not response.is_typing else "",
                                                          response.group_jid))

    def on_roster_received(self, response: FetchRosterResponse):
        print("[+] Roster:\n" + '\n'.join([str(m) for m in response.members]))

    def on_friend_attribution(self, response: chatting.IncomingFriendAttribution):
        print("[+] Friend attribution request from " + response.referrer_jid)

    def on_image_received(self, image_message: chatting.IncomingImageMessage):
        print("[+] Image message was received from {}".format(image_message.from_jid))

    def on_peer_info_received(self, response: PeerInfoResponse):
        print("[+] Peer info: " + str(response.users))

    def on_group_status_received(self, response: chatting.IncomingGroupStatus):
        print("[+] Status message in {}: {}".format(response.group_jid, response.status))

    def on_group_receipts_received(self, response: chatting.IncomingGroupReceiptsEvent):
        print("[+] Received receipts in group {}: {}".format(response.group_jid, ",".join(response.receipt_ids)))

    def on_status_message_received(self, response: chatting.IncomingStatusResponse):
        print("[+] Status message from {}: {}".format(response.from_jid, response.status))

    def on_username_uniqueness_received(self, response: UsernameUniquenessResponse):
        print("Is {} a unique username? {}".format(response.username, response.unique))

    def on_sign_up_ended(self, response: RegisterResponse):
        print("[+] Registered as " + response.kik_node)

    # Error handling

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("[-] Connection failed: " + response.message)
        self.client.loop.stop()

    def on_network_error(self, response: NetworkError):
        print("[-] Network Error: " + response.message)
        self.users = {}
        self.offset = []
        self.lock = False
        self.interval = 120
        self.client = KikClient(self, username, password, kik_node="rosa90i_bwp")

    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            # print(login_error.captcha_url)
            # sys.exit("Captcha occured")
            login_error.solve_captcha_wizard(self.client)

    def on_register_error(self, response: SignUpError):
        print("[-] Register error: {}".format(response.message))


if __name__ == '__main__':
    Read_templates()
    Read_delays()
    main()