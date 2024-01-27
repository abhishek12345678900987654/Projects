from Functions import *
import socket


def main():
    host = '127.0.0.1'
    port = 5432

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    check = client_socket.recv(128).decode()
    if check == 'C':
        fernet_key = receive_fernet_key(client_socket)
        file_format, file_format1 = receive_file_info(client_socket)
        received_data = receive_encrypted_data(client_socket)
        received_merkle_tree_root = receive_merkle_tree_root(client_socket)

        check_integrity(received_data, received_merkle_tree_root, fernet_key, file_format, file_format1)
        send_received_files(client_socket)

    elif check == 'S':
        send_received_files(client_socket)
        packet = 0
        file_path = client_socket.recv(128).decode()
        packet, fernet_key = send_fernet_key(client_socket, packet)
        packet, encrypted_data = send_encrypted_data(client_socket, file_path, fernet_key, packet)
        packet = send_merkle_tree_root(client_socket, encrypted_data, packet)

        if packet == 3:
            print('All packets have been sent successfully!')
        else:
            print("Packet Loss Detected!!")

    client_socket.close()


if __name__ == "__main__":
    main()
