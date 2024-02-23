import socket
import threading
import pickle
import os
from tkinter import *
from tkinter import messagebox
import hashlib
import sys

HEADER_LENGTH = 10
if not os.path.exists('chat logs'): os.mkdir('chat logs')  # checking if the directory exists


def input_size(variable, size):
    try:
        value = variable.get()
        if len(str(value)) > size: variable.set(str(value)[:size])  # limiting value length

    except:
        pass


class Client:

    def __init__(self, window):

        self.destination = ''

        self.online = []

        self.window = window

        self.window.configure(bg='#333333')

        self.main_frame = Frame(self.window, bg='#333333')

        # defining text variables to store values in
        self.username = StringVar()
        self.password = StringVar()

        # defining entry widgets to get input from and assigning text variables to them
        self.username_input = Entry(self.main_frame, bg='#4d4d4d', fg='white', textvariable=self.username)
        self.password_input = Entry(self.main_frame, bg='#4d4d4d', fg='white', textvariable=self.password)
        # self.username.set('emma')
        # adding  more widgets to the frame1_1
        self.username_label = Label(self.main_frame, text='Username :', fg='white', bg='#333333')
        self.password_label = Label(self.main_frame, text='Password :', fg='white', bg='#333333')

        # done configuring widgets to the credential parsing window

        # /////////////////////////////////////////////////////////////////#
        # /////////////////////////////////////////////////////////////////#

        # defining text variables to store values in
        self.server_address = StringVar()
        self.server_address.trace('w', lambda a, b, c: input_size(self.server_address, 15))

        self.server_port = IntVar()
        self.server_port.trace('w', lambda a, b, c: input_size(self.server_port, 5))

        # defining entry widgets to get input from and assigning text variables to them
        self.address_input = Entry(self.main_frame, bg='#4d4d4d', fg='white', textvariable=self.server_address)
        self.port_input = Entry(self.main_frame, bg='#4d4d4d', fg='white', textvariable=self.server_port)

        # adding  more widgets to the frame1_1
        self.address_label = Label(self.main_frame, text='Server\'s IP Address :', fg='white', bg='#333333')
        self.port_label = Label(self.main_frame, text='Server\'s Port :', fg='white', bg='#333333')

        self.back_button = Button(self.main_frame, text='Back', command=lambda: self.grid_credentials(), fg='white',
                                  bg='black')
        self.connect_button = Button(self.main_frame, text='Connect', command=lambda: self.connect(), fg='white',
                                     bg='black')

        # done configuring widgets of the connectivity details window

        # /////////////////////////////////////////////////////////////////#
        # /////////////////////////////////////////////////////////////////#

        # defining frames of the messenger window
        self.frame3_1 = LabelFrame(self.main_frame, text="Online Users", bg='#333333', fg='lime',
                                   font=('Calibri', 13, ''))
        self.frame3_2 = LabelFrame(self.main_frame, text='selectUser', bg='#333333', fg='lime')
        self.frame3_3 = Frame(self.main_frame, bg='#333333')

        # adding widgets to frame1
        self.online_users = Text(self.frame3_1, width=16, height=17, wrap=WORD, font=('Arial', 10, ''), bg='#333333',
                                 fg='lime', padx=15, pady=15, spacing1=10, spacing2=10)

        # adding widgets to frame2
        self.conversation_feed = Text(self.frame3_2, width=45, height=15, bg='#4d4d4d', wrap=WORD, fg='white',
                                      font=('Arial', 13, ''), padx=10, pady=10)

        # adding widgets to frame3
        self.message_input = Text(self.frame3_3, width=35, height=3, bg='#4d4d4d', wrap=WORD, fg='white',
                                  font=('Arial', 13, ''), padx=10, pady=10)

        self.server_button = Button(self.frame3_3, text='Toggle Server', width=10,
                                    command=lambda: self.update_labelframe('Server'))
        self.send_button = Button(self.frame3_3, text='Send', width=10, bg='black', fg='white',
                                  command=lambda: self.send())
        self.broadcast_button = Button(self.frame3_3, text='Broadcast', width=10,
                                       command=lambda: self.update_labelframe('Broadcast'))
        # done configuring widgets to the messenger window

    def grid_credentials(self):

        self.window.title('Login')

        self.main_frame.grid(row=1, column=1)

        self.username_label.grid(row=1, column=1, pady=10, padx=10, sticky=E)
        self.password_label.grid(row=2, column=1, pady=10, padx=10, sticky=E)

        self.username_input.grid(row=1, column=2, padx=10)
        self.password_input.grid(row=2, column=2, padx=10)

        self.address_label.grid(row=3, column=1, pady=10, padx=15, sticky=E)
        self.port_label.grid(row=4, column=1, pady=10, padx=15, sticky=E)

        self.address_input.grid(row=3, column=2, columnspan=2, padx=15)
        self.port_input.grid(row=4, column=2, columnspan=2, padx=15)

        self.connect_button.grid(row=5, column=3, pady=10)

    def grid_messenger(self):

        for widget in self.main_frame.winfo_children():
            widget.grid_forget()

        self.window.title(f'LAN Messenger - Welcome {self.username.get()} ! ! !')

        self.frame3_1.grid(row=1, column=1, rowspan=2)
        self.frame3_2.grid(row=1, column=2, padx=20)
        self.frame3_3.grid(row=2, column=2, sticky=N)

        self.online_users.bind('<Triple-Button-1>', lambda a: self.update_labelframe(self.online_users.selection_get()))
        self.online_users.grid(row=0, column=1)

        self.conversation_feed.grid(row=0, column=1)

        self.message_input.bind('<Shift-Return>', lambda e: self.send())
        self.message_input.grid(row=0, column=0, columnspan=4, pady=10)

        self.server_button.grid(row=1, column=0)
        self.send_button.grid(row=1, column=1, pady=10)
        self.broadcast_button.grid(row=1, column=2)

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client.connect((self.server_address.get(), self.server_port.get()))   # connecting to server ("127.0.0.1",1234))#
        self.thread1 = threading.Thread(target=self.receiv)                     # starting listening thread
        self.thread1.start()

        information_dict = {'name': self.username.get(), 'password': self.hash(self.password.get())}  # preparing credentials
        message = pickle.dumps(information_dict)
        sende = bytes(f"{len(message):<{HEADER_LENGTH}}", "utf-8") + message
        self.client.send(sende)             # sending credentials

    def send(self):
        text = self.message_input.get('1.0', END)

        # preparing dictionary
        deliver_dict = {'source': self.username.get(), 'destination': self.destination, 'data': text}

        message = pickle.dumps(deliver_dict)
        self.sende = bytes(f"{len(message):<{HEADER_LENGTH}}", "utf-8") + message
        self.client.send(self.sende)
        self.write_log(deliver_dict['destination'], f'\nYou: {text}')
        self.conversation_feed.insert(END, f'\nYou: {text}')
        self.message_input.delete('1.0', END)

    def receiv(self):
        while True:
            try:
                header = self.client.recv(HEADER_LENGTH).decode("utf-8")
                message = pickle.loads(self.client.recv(int(header)))

                if message['source'] == 'SERVER':

                    if message['type'] == 'auth':
                        if message['data'] == 'granted':
                            self.grid_messenger()
                        else:
                            messagebox.showinfo(title="Error", message='Username or password is wrong')

                    if message['type'] == 'state':
                        if message['data'] == 'off':
                            messagebox.showinfo(title="server offline", message='Server is offline')
                            root.quit()
                            break

                    if message['type'] == 'updates':

                        username = message['data']['username']
                        status = message['data']['status']

                        if status == 'online':
                            self.online.append(username)
                            self.online_users.delete('1.0', END)
                            for user in self.online: self.online_users.insert(END, f'{user}\n')

                        else:
                            self.online.remove(username)
                            self.online_users.delete('1.0', END)
                            for user in self.online: self.online_users.insert(END, f'{user}\n')

                    if message['type'] == 'Broadcast':

                        self.write_log(message['type'], f"{message['data']['username']}~ {message['data']['data']}")
                        if message['type'] == self.frame3_2['text']:
                            self.conversation_feed.insert(END,
                                                          f"\n {message['data']['username']}~ {message['data']['data']}")


                else:

                    self.write_log(message['source'], f"{message['source']}: {message['data']}")
                    if message['source'] == self.frame3_2['text']:
                        self.conversation_feed.insert(END, f"\n{message['source']}: {message['data']}")
            except:
                sys.exit()

    def update_labelframe(self, username):
        self.frame3_2.configure(text=username)
        self.destination = username

        if os.path.exists(f'chat logs/{username}.txt'):
            data = self.read_log(username)
            self.conversation_feed.delete('1.0', END)
            self.conversation_feed.insert(END, data)
        else:
            newfile = open(f'chat logs/{username}.txt', 'w')
            newfile.close()

            self.conversation_feed.delete('1.0', END)
            self.conversation_feed.insert(END, 'say hello!!\n')

    def write_log(self, filename, data):
        file = open(f'chat logs/{filename}.txt', 'a')
        file.write(f'{data.strip()}\n')
        file.close()

    def read_log(self, filename):
        file = open(f'chat logs/{filename}.txt', 'r')
        data = file.read()
        return data

    def hash(self, password):
        password = hashlib.md5(password.encode())
        return password.hexdigest()


if __name__ == '__main__':
    root = Tk()
    client1 = Client(root)

    client1.grid_credentials()

    root.mainloop()
