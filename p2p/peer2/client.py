# Computer Networks HW3 | Spring 2020 - Done by Adilet Askerov & Nazym Altayeva
# Peer Client

from tkinter import *
from tkinter.ttk import Treeview

import datetime
import socket
import threading
import pickle
import os

my_ip = ''
my_port = 0

local_files = []

def getLocalFiles(mypath, ip, port):
    files = []

    with os.scandir(mypath) as dir_entries:
        for entry in dir_entries:
            if entry.is_file():
                info = entry.stat()
                name = entry.name.split('.',1)
                file_data = [name[0], name[1], str(info.st_size), str(datetime.datetime.fromtimestamp(info.st_mtime).strftime('%d/%m/%Y')), ip, port]
                files.append(file_data)
                local_files.append(file_data)
            elif entry.is_dir():
                files.append(entry.name)

    if len(files) > 5:
        return files[:5]
    else:
        return files

def connectToPeer(file_info):
    ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ds.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = file_info[-2]
    port = int(file_info[-1])
    
    ds.connect((host,port))

    ds.send(bytes("DOWNLOAD:" + file_info[0] + "," + file_info[1] + "," + file_info[2], "utf-8"))

    filename = file_info[0] + "." + file_info[1]

    f = open('new_' + filename, 'wb')
    data = ds.recv(1024)
    total_recvd = len(data)
    f.write(data)

    while total_recvd < int(file_info[2]):
        data = ds.recv(1024)
        total_recvd += len(data)
        f.write(data)
    print("Download complete.")

    ds.close()
    


def sendRequestedFile(conn, addr):
    msg = conn.recv(1024).decode("utf-8")

    if msg[:8] == "DOWNLOAD":
        info = msg[9:].split(',')

        filename = info[0] + "." + info[1]

        with open(filename, 'rb') as f:
            bytesToSend = f.read(1024)
            conn.send(bytesToSend)
            while bytesToSend != "":
                bytesToSend = f.read(1024)
                conn.send(bytesToSend)
            print("Sending complete.")

    conn.close()



def listen(ip, port):
    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    print("LISTEN")
    print("IP =", ip)
    print("My Port =", port)

    ls.bind((ip,port))
    
    ls.listen(5)

    while True:
        conn, addr = ls.accept()
        print("<", addr, "> has connected to me")

        th = threading.Thread(target=sendRequestedFile, args=(conn, addr))
        th.start()

    ls.close()

def Main():
    '''
    window = Tk()
    window.title("P2P File Sharing")
    #window.geometry("600x600")
    window.resizable(0,0)
    window.configure(background = "#EDEEEF")

    # image
    photo1 = PhotoImage(file = "P2P-network.png")
    Label(window, image = photo1, bg = "#EDEEEF").grid(row = 0, column = 0, sticky = W+E+N+S)

    # labels
    Label(window, text = "File name:", width = 0, bg = "#EDEEEF", fg = "black", 
    font = "none 14").grid(row = 1, column = 0, sticky = W, padx = 10)

    Label(window, text = "Message", width = 0, bg = "#EDEEEF", fg = "black", 
    font = "none 14").grid(row = 2, column = 0)

    # text box
    texte = Entry(window, width = 19)
    texte.grid(row = 1, column = 0)

    # download text
    dwnld = Entry(window, width = 25)
    dwnld.grid(row = 5, column = 0, padx = 20, pady = 10)

    # buttons
    Button(window, text = "Search", width = 8, 
    bg = "#EDEEEF").grid(row = 1, column = 0, sticky = E, padx = 20)

    Button(window, text = "Download", width = 8, 
    bg = "#EDEEEF").grid(row = 4, column = 0, padx = 20)

    # treeview
    tree = Treeview(window)

    tree["columns"] = ("one", "two", "three")
    tree.column("#0", width=170, minwidth=120, stretch = NO)
    tree.column("one", width=130, minwidth=100, stretch = NO)
    tree.column("two", width=90, minwidth=60)
    tree.column("three", width=80, minwidth=50, stretch = NO)
    tree.column("four", width=80, minwidth=50, stretch = NO)
    tree.column("five", width=80, minwidth=50, stretch = NO)

    tree.heading("#0",text="Name",anchor = W)
    tree.heading("one", text="Type",anchor = W)
    tree.heading("two", text="Size",anchor = W)
    tree.heading("three", text="Modify",anchor = W)
    tree.heading("four", text="IP",anchor = W)
    tree.heading("five", text="Port",anchor = W)
    
    #tree.insert("", 2, text="text_file.txt", values=("23-Jun-17 11:25","TXT file","1 KB"))

    tree.grid(row = 3, column = 0, padx = 10, pady = 15)
    '''

    ### CONNECTION WITH THE SERVER
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = socket.gethostname()
    port = 8080

    s.connect((host, port))

    ip, portt = s.getsockname()

    my_ip, my_port = ip, portt

    # listening for other peers
    thr = threading.Thread(target=listen, args=(my_ip, my_port))
    thr.start()

    # Hello -> Hi
    s.send(bytes("HELLO", "utf-8"))
    response = s.recv(1024).decode("utf-8")

    if response == "HI":
        
        files = getLocalFiles(os.getcwd(), my_ip, my_port)
        print("Sending list of files...")
        s.send(pickle.dumps(files))

        msg = s.recv(1024).decode("utf-8")

        if msg == "ACCEPTED":
            # LOOP to request files
            filename = input(str("Filename?(type 'exit' to quit the program) ->)"))
            while filename != 'exit':
                s.send(bytes("SEARCH:" + filename, "utf-8"))
                print("Waiting for search results...")

                search = s.recv(1024).decode("utf-8")
                print("search =", search)
                if search == "FOUND:":
                    src = s.recv(1024)
                    search_results = pickle.loads(src)
                    print("RESULTS:")
                    for f in search_results:
                        print(f)
                    file_info = input(str("Enter needed file's name, type, size, ip and port|-> name,type,size,ip,port ="))
                    
                    if file_info != 'exit':
                        req_file = file_info.split(',')
                        print("REQ_FILE = ", req_file)
                        print("Connecting to entered peer...")
                        connectToPeer(req_file)
                    else:
                        filename = file_info

                    filename = input(str("File found. Enter other file? ->"))
                else:
                    print("FILE NOT FOUND. Please enter another name \n")
                    filename = input(str("Filename?(type 'exit' to quit the program) ->)"))
                    

            print("Exit confirmed")
            s.send(bytes("BYE", "utf-8"))
            s.close()
        else:
            s.close()
    s.close()

    # run the main loop
    #window.mainloop()

if __name__ == '__main__':
    Main()