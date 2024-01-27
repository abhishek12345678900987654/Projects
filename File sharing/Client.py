from Functions import *
import socket


def main():
    host = '127.0.0.1'
    port = 5432

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print("File Transfer from Which Side:")
    print("(S) Server")
    print("(C) Client")
    check = input("-> ")
    client_socket.send(check.encode())

    if check.lower() == 'c':
        file_path = interface()

        packet = 0
        packet, fernet_key = send_fernet_key(client_socket, packet)
        packet = fileinfo(client_socket, file_path, packet)
        packet, encrypted_data = send_encrypted_data(client_socket, file_path, fernet_key, packet)
        packet = send_merkle_tree_root(client_socket, encrypted_data, packet)

        if packet == 4:
            print('All packets have been sent successfully!')
        else:
            print("Packet Loss Detected!!")

        view_serverfiles(client_socket)

    elif check.lower() == 's':
        view_serverfiles(client_socket)
        print()
        print("Choose the file you want to Download: ")
        file_path = input('-> ')
        file_format = file_path.split('.')[0]
        file_format1 = file_path.split('.')[-1]

        client_socket.send(file_path.encode())
        fernet_key = receive_fernet_key(client_socket)
        received_data = receive_encrypted_data(client_socket)
        received_merkle_tree_root = receive_merkle_tree_root(client_socket)
        check_integrity(received_data, received_merkle_tree_root, fernet_key, file_format, file_format1)

    client_socket.close()


if __name__ == "__main__":
    main()
