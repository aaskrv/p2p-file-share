# FT Server

import socket
import pickle
import threading
import os
from collections import defaultdict

all_files = defaultdict(list)
online_users = []

def RetrieveFiles(sock, addr):
    msg = sock.recv(1024).decode("utf-8")

    client_port = 0
    if msg == "HELLO":
        sock.send(bytes("HI", "utf-8"))

        print("Receiving list of files...")
        files_info = sock.recv(1024)
        files_arr = pickle.loads(files_info)
        print("Received the files list.")

        if len(files_arr) != 0:
            for f in files_arr:
                all_files[f[0]].append(f[1:])
                if f[-1] not in online_users:
                    client_port = f[-1]
                    online_users.append(client_port)
            
            print("List of available files updated: ")
            file_table = dict(all_files)
            for i in file_table:
                print(i, '-', file_table[i])

            sock.send(bytes("ACCEPTED", "utf-8"))

            # File request LOOP
            file_request = sock.recv(1024).decode("utf-8")
            print("REQUEST = ", file_request)
            print("USERS =", online_users)
            while(file_request != "BYE"):
                if len(file_request) > 3 and file_request[:6] == "SEARCH":
                    req = file_request[7:]
                    print("File:",req, "requested")
                    if client_port in online_users:
                        search_db = dict(all_files)
                        file_occurrences = search_db.get(req)
                        print("Occurr = ", file_occurrences)
                    
                        if file_occurrences != None:
                            arr = str(file_occurrences)
                            sock.send(bytes("FOUND:", "utf-8"))
                            sock.send(pickle.dumps(file_occurrences))
                            file_request = sock.recv(1024).decode("utf-8")
                        else:
                            sock.send(bytes("NOT FOUND", "utf-8"))
                            file_request = sock.recv(1024).decode("utf-8")
                        

            online_users.remove(client_port)
            sock.close()
        else:
            sock.send(bytes("REJECTED", "utf-8"))
            sock.close()
    print("Bye bye")
    print(online_users)
    sock.close()
    
def Main():
    host = socket.gethostname()
    port = 8080

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    
    s.listen(5)
    print("Server waiting for incoming connections...")

    while True:
        conn, addr = s.accept()
        print("<", addr, "> has connected to the server")

        th = threading.Thread(target=RetrieveFiles, args=(conn,addr))
        th.start()

    s.close()

if __name__ == '__main__':
    Main()
