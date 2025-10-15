import socket
import threading
import datetime

HOST = '127.0.0.1'
PORT = 5050
STORE = {} # Key-Value store
UPTIME = datetime.datetime.now()
REQUEST_COUNT = 0

def log_request(addr, request, response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Client {addr}: Request='{request.strip()}', Response='{response.strip()}'")

def handle_client(conn, addr):
    global REQUEST_COUNT
    print(f"[NEW CONNECTION] {addr} connected.")
    
    connected = True
    while connected:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            REQUEST_COUNT += 1
            request_line = data.strip()
            parts = request_line.split(' ')

            response = ""
            if len(parts) < 2 or parts[0] != "KV/1.0":
                response = "426 UPGRADE_REQUIRED\n"
            else:
                command = parts[1]
                
                if command == "PUT":
                    if len(parts) >= 4:
                        key = parts[2]
                        value = " ".join(parts[3:])
                        if key in STORE:
                            STORE[key] = value
                            response = "200 OK\n"
                        else:
                            STORE[key] = value
                            response = "201 CREATED\n"
                    else:
                        response = "400 BAD_REQUEST\n"
                elif command == "GET":
                    if len(parts) >= 3:
                        key = parts[2]
                        if key in STORE:
                            response = f"200 OK {STORE[key]}\n"
                        else:
                            response = "404 NOT_FOUND\n"
                    else:
                        response = "400 BAD_REQUEST\n"
                elif command == "DEL":
                    if len(parts) >= 3:
                        key = parts[2]
                        if key in STORE:
                            del STORE[key]
                            response = "204 NO_CONTENT\n"
                        else:
                            response = "404 NOT_FOUND\n"
                    else:
                        response = "400 BAD_REQUEST\n"
                elif command == "STATS":
                    uptime_seconds = (datetime.datetime.now() - UPTIME).total_seconds()
                    response = f"200 OK keys={len(STORE)} uptime={int(uptime_seconds)}s served={REQUEST_COUNT}\n"
                elif command == "QUIT":
                    response = "200 OK bye\n"
                    connected = False
                else:
                    response = "400 BAD_REQUEST\n"

            conn.sendall(response.encode('utf-8'))
            log_request(addr, request_line, response)

        except ConnectionResetError:
            print(f"[DISCONNECTED] {addr} forcibly disconnected.")
            connected = False
        except Exception as e:
            print(f"[ERROR] {addr}: {e}")
            response = "500 SERVER_ERROR\n"
            conn.sendall(response.encode('utf-8'))
            log_request(addr, request_line if 'request_line' in locals() else "N/A", response)
            connected = False

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()