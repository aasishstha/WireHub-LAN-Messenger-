from tkinter import *
from tkinter import ttk, messagebox
import server                          # imports server module from same directory
import threading
import hashlib


class Server_GUI:

    def __init__(self, window):

        self.obj = server.server_class()

        self.db_op = server.db_operations()

        self.window = window
        self.window.title("Server login")

        style = ttk.Style(window)
        style.configure('TNotebook.Tab', padding=(10, 15), width=10, font=('Arial Rounded MT Bold', 12))

        self.frame1 = Frame(self.window)
        self.frame1.grid(row=0, column=0)

        # Defining variable to contain admin's username and password
        self.admin_username = StringVar()
        self.admin_password = StringVar()

        # admin login######################################
        self.admin_username_entry = ttk.Entry(self.frame1, width=35, textvariable=self.admin_username)
        self.admin_username_entry.grid(row=0, column=0, padx=15, pady=15)
        self.admin_password_entry = ttk.Entry(self.frame1, width=35, textvariable=self.admin_password)
        self.admin_password_entry.grid(row=1, column=0, padx=15, pady=15)
        self.login_button = ttk.Button(self.frame1, text='login', command=lambda: self.login(), width=15,
                                       padding=(0, 5))
        self.login_button.grid(row=2, column=0, padx=15, pady=25)

        # admin panel######################################
        self.start_button = Button(self.window, text='Start Server', width=25, bg='green', fg='white',
                                   command=lambda: self.server_trigger())

        self.frame2 = Frame(self.window, bg='#333333')

        notebook = ttk.Notebook(self.frame2)
        # add or remove users panel########################
        tab1 = ttk.Frame(notebook, padding=(10, 10))

        # Defining variable to contain user's username and password
        self.username = StringVar()
        self.password = StringVar()

        username_entry = ttk.Entry(tab1, width=25, textvariable=self.username)
        username_entry.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        password_entry = ttk.Entry(tab1, width=25, textvariable=self.password)
        password_entry.grid(row=1, column=0, padx=15, pady=15, columnspan=2)

        add_button = ttk.Button(tab1, text='Add Users', width=15,
                                padding=(0, 5), command=lambda: self.db_op.add_user(self.username.get(),
                                                                                    self.hash(self.password.get())))
        add_button.grid(row=2, column=0, padx=5, pady=15)

        remove_button = ttk.Button(tab1, text='Remove Users', width=15,
                                   padding=(0, 5), command=lambda: self.db_op.remove_user(self.username.get(),
                                                                                          self.hash(
                                                                                              self.password.get())))
        remove_button.grid(row=2, column=1, padx=5, pady=15)

        # Promote users###########################################

        tab2 = ttk.Frame(notebook, padding=(10, 10))

        username_entry2 = ttk.Entry(tab2, width=25, textvariable=self.username)
        username_entry2.grid(row=0, column=0, padx=15, pady=15, columnspan=2)

        promote_button = ttk.Button(tab2, text='Promote User', width=15, padding=(0, 5),
                                    command=lambda: self.db_op.set_privilage(self.username.get(), 'increase'))
        promote_button.grid(row=2, column=0, padx=5, pady=15)

        demote_button = ttk.Button(tab2, text='Demote User', width=15, padding=(0, 5),
                                   command=lambda: self.db_op.set_privilage(self.username.get(), 'decrease'))
        demote_button.grid(row=2, column=1, padx=5, pady=15)

        # ban users#########################################################

        tab3 = ttk.Frame(notebook, padding=(10, 10))

        username_entry3 = ttk.Entry(tab3, width=25, textvariable=self.username)
        username_entry3.grid(row=0, column=0, padx=15, pady=15)

        ban_button = ttk.Button(tab3, text='Ban User', width=15, padding=(0, 5),
                                command=lambda: self.db_op.set_privilage(self.username.get(), 'bann'))
        ban_button.grid(row=1, column=0, padx=5, pady=15)

        # logs#########################################################

        tab4 = ttk.Frame(notebook, padding=(10, 10))

        log_type = StringVar()
        options = ('Active Users', 'Events')
        action_dropdown = ttk.Combobox(tab4, textvariable=log_type, state='readonly', width=25,
                                       values=options)
        action_dropdown.grid(row=0, column=0, padx=15, pady=15)
        action_dropdown.bind('<<ComboboxSelected>>', lambda a: self.logs(log_type.get()))

        self.textbox = Text(tab4, width=65, height=7)
        self.textbox.grid(row=1, column=0, padx=10, pady=10)

        # self.open_button = ttk.Button(tab4, text='Open',width=15, padding=(0, 5),command=lambda :self.open_event)

        notebook.add(tab1, text="Add/Remove")
        notebook.add(tab2, text="Promote")
        notebook.add(tab3, text="Ban")
        notebook.add(tab4, text="Logs")

        notebook.grid(row=0, column=0)

    def login(self):
        if self.db_op.get_privilage(self.admin_username.get()) == 3: # checking privilege before parsing password
            credentials = {'name': self.admin_username.get(), 'password': self.hash(self.admin_password.get())}
            if self.db_op.authenticate(credentials):
                self.frame1.grid_remove()
                self.start_button.grid(row=0, column=0, pady=20)
                self.frame2.grid(row=1, column=0)
            else:
                messagebox.showerror(title="Error", message='Username or password is wrong')
        else:
            messagebox.showerror(title="Error", message="You're not admin")

    def server_trigger(self):
        mode = self.start_button['text']
        if mode == 'Start Server':
            self.thread1 = threading.Thread(target=self.obj.start_server)   # Thread to start server

            self.thread1.start()
            self.start_button['text'] = "Stop Server"
            self.start_button['bg'] = 'red'

        else:
            # self.thread2 = threading.Thread(target=self.obj.stop)
            # self.thread2.start()
            self.obj.stop()                     # Calling function to stop server
            self.start_button['text'] = "Start Server"
            self.start_button['bg'] = 'green'
            self.start_button['fg'] = 'white'           # making changes to the button after stopping server


    def logs(self, log_type):

        if log_type == "Active Users":
            self.textbox.delete('1.0', END)

            users = self.obj.clients            # parsing online clients username
            for key, value in users.items():
                self.textbox.insert(END, f'{value["name"]}\n')  # inserting values in the textbox

        else:
            self.textbox.delete('1.0', END)
            logfile = open("events.txt", 'r')
            self.textbox.insert(END, logfile.read())
            logfile.close()

    def hash(self, password):
        password = hashlib.md5(password.encode())
        return password.hexdigest()             # returning the calculated hash value of password


if __name__ == '__main__':          # checking if program is executed as primary process
    root = Tk()                     # making Tkinter object
    client1 = Server_GUI(root)      # Passing object to the gui class to add widgets and form a proper GUI

    root.mainloop()
