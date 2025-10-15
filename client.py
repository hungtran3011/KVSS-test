import socket
import sys

HOST = '127.0.0.1'
PORT = 5050

def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(request.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(response.strip())
        except ConnectionRefusedError:
            print("Error: Connection refused. Make sure the server is running.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print(f"KVSS Client connected to {HOST}:{PORT}")
    print("Enter commands (e.g., KV/1.0 PUT key value, KV/1.0 GET key, KV/1.0 DEL key, KV/1.0 STATS, KV/1.0 QUIT):")
    print("Type 'exit' to quit the client.")

    while True:
        try:
            command = input("> ")
            if command.lower() == 'exit':
                break
            
            # Add newline character if not already present, as per protocol
            if not command.endswith('\n'):
                command += '\n'
            
            send_request(command)

        except KeyboardInterrupt:
            print("\nExiting client.")
            break
        except EOFError:
            print("\nExiting client due to EOF.")
            break