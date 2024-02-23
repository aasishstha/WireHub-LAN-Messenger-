import socket
import threading
import pickle
import datetime
import pymysql
from tkinter import messagebox


HEADER_LENGTH = 10
server_address = "0.0.0.0" #"127.0.0.1"  
port = 1234
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_address, port))
server.listen()


# clients = {}


class db_operations:

    def __init__(self):
        self.mydb = pymysql.connect(host='localhost', user='root', password='green', database='dbfyp')

        self.mycursor = self.mydb.cursor()

    def authenticate(self, credentials):
        username = credentials['name']
        password = credentials['password']
        if self.validate_user(username):
            self.mycursor.execute(f"select pass from users where user_id='{username}'")
            if self.mycursor.fetchone()[0] == password:
                return True
            else:
                return False
        else:
            return False

    def add_user(self, name, key):
        self.mycursor.execute(f"insert into users values('{name}','{key}',1)")
        self.mydb.commit()
        messagebox.showinfo(title="Done", message="User added")



    def remove_user(self, name, key):
        self.mycursor.execute(f"delete from users where user_id='{name}'")
        self.mydb.commit()
        messagebox.showinfo(title="Done", message="User removed")

    def validate_user(self, user):

        self.mycursor.execute(f'select count(user_id) from users where user_id="{user}"')

        return int(self.mycursor.fetchone()[0])

    def get_privilage(self, name):
        self.mycursor.execute(f'select privilage from users where user_id="{name}"')
        privilege = self.mycursor.fetchone()
        return int(privilege[0])

    def set_privilage(self, id, todo):
        privilege = self.get_privilage(id)

        if todo == 'increase':
            if privilege < 3:
                self.mycursor.execute(f'update users set privilage={privilege + 1} where user_id="{id}"')
                self.mydb.commit()
                messagebox.showinfo(title="Done", message=f"{id} privilege set to {privilege + 1}")
            else:
                messagebox.showwarning(title="Error", message=f"privilege cannot exceed {privilege}")

        elif todo == 'decrease':
            if privilege > 1:
                self.mycursor.execute(f'update users set privilage={privilege - 1} where user_id="{id}"')
                self.mydb.commit()
                messagebox.showinfo(title="Done", message=f"{id} privilege set to {privilege - 1}")
            else:
                messagebox.showwarning(title="Error", message=f"privilege cannot be below {privilege} unless banned")

        else:
            self.mycursor.execute(f'update users set privilage=0 where user_id="{id}"')
            self.mydb.commit()
            messagebox.showinfo(title="Done", message=f"{id} privilege set to {self.get_privilage(id)}")

    '''def create_group(self,name, admin, key, members):
        mydb4 = pymysql.connect(host='localhost', user='root', password='green', database='dbfyp')

        mycursor4 = mydb4.cursor()
        values=((name, admin, key, members),)
        print(values)
        try:
            mycursor4.execute(
    f'insert into broadcast(group_id, group_admin, pass, members) values("{name}","{admin}","{key}","{members}")')
            mydb4.commit()
        except Exception as e:
            print(e)
        mydb4.close()'''

    def get_admin(self, group):
        self.mycursor.execute(f'select group_admin from broadcast where group_id="{group}"')
        return self.mycursor.fetchone()[0]

    def get_key(self, group):
        self.mycursor.execute(f'select pass from broadcast where group_id="{group}"')
        return self.mycursor.fetchone()[0]

    def purge_group(self, group):
        self.mycursor.execute(f'delete from broadcast where group_id="{group}"')
        self.mydb.commit()
        print('purged')


class server_class():

    def __init__(self):
        self.clients = {}

    def forward(self, data_dict):
        dict_dump = pickle.dumps(data_dict)
        data = bytes(f"{len(dict_dump):<{HEADER_LENGTH}}", "utf-8") + dict_dump
        for client in self.clients:
            if data_dict['destination'] == self.clients[client]['name']:
                client.send(data)
                break

            elif data_dict['destination'] == 'Server':
                db_ops = db_operations()

                source = data_dict['source']
                privilage = db_ops.get_privilage(source)
                command = list((data_dict['data']).split())

                if privilage >= 1:
                    if (command[0]).lower() == 'create':

                        if (command[1]).lower() == 'group' and len(command) == 6 and db_ops.validate_user(command[4]):
                            name = command[2]
                            key = command[3]
                            admin = command[4]
                            members = command[5]
                            #db_ops.create_group(name,key,admin,members)
                            mydb4 = pymysql.connect(host='localhost', user='root', password='green', database='dbfyp')

                            mycursor4 = mydb4.cursor()
                            values = ((name, admin, key, members),)
                            try:
                                mycursor4.execute(
                                    f'insert into broadcast(group_id, group_admin, pass, members) values("{name}","{admin}","{key}","{members}")')
                                mydb4.commit()
                            except Exception as e:
                                print(e)
                            mydb4.close()

                        # creation integrations to be added here in future

                        else:
                            print('syntax error')


                    elif (command[0]).lower() == 'purge':

                        if (command[1]).lower() == 'group' and len(command) == 4:
                            group = command[2]
                            key = command[3]
                            if source == db_ops.get_admin(group) and key == db_ops.get_key(group):
                                db_ops.purge_group(group)

                        # purge integrations to be added here in future

                        else:
                            print('Syntax error')


                    elif (command[0]).lower() == 'bann' and len(command) == 2:
                        id = command[1]
                        if db_ops.get_privilage(source) == 3:
                            db_ops.set_privilage(id, 0)
                        else:
                            print('not privilaged enough')


                    else:
                        print('syntax error')
                else:
                    print('youre not privilaged enough')

                break

            elif data_dict['destination'] == 'Broadcast':
                data_dict2 = {'source': 'SERVER', 'type': 'Broadcast',
                              'data': {'username': data_dict['source'], 'data': data_dict['data']}}
                dict2_dump = pickle.dumps(data_dict2)
                message = bytes(f"{len(dict2_dump):<{HEADER_LENGTH}}", "utf-8") + dict2_dump
                for client in self.clients:
                    if data_dict['source'] != self.clients[client]['name']:
                        client.send(message)
                break



            else:
                continue

    def handle(self, client_socket, client_address):
        username = self.clients[client_socket]['name']
        information_dict = {'source': 'SERVER', 'type': 'auth', 'data': 'granted', 'destination': username}
        self.forward(information_dict)

        while True:
            try:
                header = client_socket.recv(HEADER_LENGTH).decode('utf-8')
                data = client_socket.recv(int(header))
                incoming_dict = pickle.loads(data)

                self.forward(incoming_dict)

            except:
                self.state_broadcast(client_socket, 'disconnected')
                del self.clients[client_socket]
                print(f"client list after: {self.clients}")
                break

    def state_broadcast(self, socket, status):
        address = (str(socket).split("=")[-1][:-1])[1:-1].split(
            ',')  # formatting socket as string to obtain address & port
        username = self.clients[socket]['name']

        if status == 'connected':
            logfile = open("events.txt", 'a')
            logfile.write(
                f"{username} connected ip: {address[0]} port: {address[1].strip()} timestamp: {datetime.datetime.now()}\n")
            logfile.close()
            print((
                      f"{username} connected ip: {address[0]} port: {address[1].strip()} timestamp: {datetime.datetime.now()}"))

            information_dict = {'source': 'SERVER', 'type': 'updates',
                                'data': {'username': username, 'status': 'online'}}
            message = pickle.dumps(information_dict)

            for client in self.clients:
                if username != self.clients[client]['name']:
                    sende = bytes(f"{len(message):<{HEADER_LENGTH}}", "utf-8") + message
                    client.send(sende)

                else:
                    for socket, data in self.clients.items():

                        if username != data['name']:
                            information_dict = {'source': 'SERVER', 'type': 'updates',
                                                'data': {'username': data['name'], 'status': 'online'}}
                            message = pickle.dumps(information_dict)
                            sende = bytes(f"{len(message):<{HEADER_LENGTH}}", "utf-8") + message
                            client.send(sende)




        elif status == 'disconnected':
            logfile = open("events.txt", 'a')
            logfile.write(
                f"{username} disconnected ip: {address[0]} port: {address[1].strip()} timestamp: {datetime.datetime.now()}\n")
            logfile.close()
            print(
                f"{username} disconnected ip: {address[0]} port: {address[1].strip()} timestamp: {datetime.datetime.now()}")

            information_dict = {'source': 'SERVER', 'type': 'updates',
                                'data': {'username': username, 'status': 'offline'}}
            message = pickle.dumps(information_dict)

            for client in self.clients:
                if username != self.clients[client]['name']:
                    sende = bytes(f"{len(message):<{HEADER_LENGTH}}", "utf-8") + message
                    client.send(sende)
                else:
                    pass

    def start_server(self):
        while True:


            client_socket, client_address = server.accept()

            try:
                credentials_header = client_socket.recv(HEADER_LENGTH).decode("utf-8")
                if credentials_header == "STOP":
                    break
                else:
                    credentials = client_socket.recv(int(credentials_header))
                    self.credentials_dict = pickle.loads(credentials)
                    print(self.credentials_dict)
                    self.auth = db_operations().authenticate(self.credentials_dict)

            except:
                continue
            if self.auth:
                self.clients[client_socket] = self.credentials_dict
                self.state_broadcast(client_socket, 'connected')
                client_thread = threading.Thread(target=self.handle, args=((client_socket, client_address)))
                client_thread.start()
            else:
                username = self.credentials_dict['name']
                information_dict = {'source': 'SERVER', 'type': 'auth', 'data': 'denied', 'destination': username}
                dict_dump = pickle.dumps(information_dict)
                data = bytes(f"{len(dict_dump):<{HEADER_LENGTH}}", "utf-8") + dict_dump
                client_socket.send(data)

    def stop(self):
        data_dict2 = {'source': 'SERVER', 'type': 'state',
                      'data': "off"}
        dict2_dump = pickle.dumps(data_dict2)
        message = bytes(f"{len(dict2_dump):<{HEADER_LENGTH}}", "utf-8") + dict2_dump
        for client in self.clients:
            # if data_dict['source'] != clients[client]['name']:
            client.send(message)
        # self.a=False
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2.connect(('127.0.0.1', 1234))
        client2.send(bytes("STOP", "utf-8"))

