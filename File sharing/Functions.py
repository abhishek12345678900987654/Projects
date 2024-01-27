import os
import hashlib
from cryptography.fernet import Fernet


# Functions For Building Merkle Tree
def hash_value(data):
    return hashlib.sha256(data).digest()


def build_merkle_tree_rec(nodes):
    if len(nodes) % 2 == 1:
        nodes.append(nodes[-1])
    half = len(nodes) // 2

    if len(nodes) == 2:
        return hash_value(nodes[0] + nodes[1])
    left = build_merkle_tree_rec(nodes[:half])
    right = build_merkle_tree_rec(nodes[half:])
    return hash_value(left + right)


def build_merkle_tree(values):
    leaves = [hash_value(e) for e in values]
    if len(leaves) % 2 == 1:
        leaves.append(leaves[-1])
    return build_merkle_tree_rec(leaves)


# Encryption and Decryption
def decrypt_file(encrypted_data, fernet_key):
    fernet = Fernet(fernet_key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data


def encrypt_file(file_path, fernet_key):
    with open(file_path, 'rb') as file:
        plaintext = file.read()

    fernet = Fernet(fernet_key)
    ciphertext = fernet.encrypt(plaintext)

    return ciphertext


# Client.py Functions
def send_fernet_key(client_socket, packet):
    fernet_key = Fernet.generate_key()
    client_socket.sendall(fernet_key)
    packet = receive_ack(client_socket, packet)
    return packet, fernet_key


def fileinfo(client_socket, file_path, packet):
    file_format = file_path.split('.')[0]
    client_socket.send(file_format.encode())
    file_format1 = file_path.split('.')[-1]
    client_socket.send(file_format1.encode())
    packet = receive_ack(client_socket, packet)

    return packet


def send_encrypted_data(client_socket, file_path, fernet_key, packet):
    encrypted_data = encrypt_file(file_path, fernet_key)
    client_socket.sendall(encrypted_data)
    packet = receive_ack(client_socket, packet)

    return packet, encrypted_data


def send_merkle_tree_root(client_socket, encrypted_data, packet):
    merkle_tree_root = build_merkle_tree([encrypted_data])
    client_socket.sendall(merkle_tree_root)
    packet = receive_ack(client_socket, packet)

    return packet


def receive_ack(client_socket, packet):
    ack = client_socket.recv(3)
    if ack == b"ACK":
        packet = packet + 1
    return packet


# Server.py Functions
def receive_fernet_key(client_socket):
    fernet_key = client_socket.recv(44)
    send_ack(client_socket, b"ACK")

    return fernet_key


def receive_file_info(client_socket):
    file_format = client_socket.recv(128).decode()
    file_format1 = client_socket.recv(128).decode()
    send_ack(client_socket, b"ACK")

    return file_format, file_format1


def receive_encrypted_data(client_socket):
    received_data = client_socket.recv(214748899)
    send_ack(client_socket, b"ACK")

    return received_data


def receive_merkle_tree_root(client_socket):
    received_merkle_tree_root = client_socket.recv(64)
    send_ack(client_socket, b"ACK")

    return received_merkle_tree_root


def check_integrity(received_data, received_merkle_tree_root, fernet_key, file_format, file_format1):
    server_merkle_tree_root = build_merkle_tree([received_data])

    if received_merkle_tree_root == server_merkle_tree_root:
        decrypted_data = decrypt_file(received_data, fernet_key)

        file_path = f'{file_format}.{file_format1}'
        save_file(decrypted_data, file_path)
        print()
        print(f"File saved as {file_path}")

    else:
        print("File integrity check failed. The received file may be corrupted.")


def send_ack(client_socket, ack_message):
    client_socket.send(ack_message)


def send_received_files(client_socket):
    sent_filenames = []

    files = list_files()
    for filename in files:
        if str(filename) != "DSA_Project Server.py" and str(filename) != "Functions.py":
            sent_filenames.append(filename)

    sent_filenames_str = "\n".join(sent_filenames)
    client_socket.sendall(sent_filenames_str.encode())


# Secondary Functions
def interface():
    sent_filenames = []
    files = list_files()
    for filename in files:
        if str(filename) != "DSA_Project Client.py" and str(filename) != "Functions.py":
            sent_filenames.append(filename)
    sent_filenames_str = "\n".join(sent_filenames)
    print("Files present")
    print(sent_filenames_str)

    print("Enter the file You Wish to Send")
    file_path = input("-> ")

    return file_path


def view_serverfiles(client_socket):
    sent_filenames = client_socket.recv(1024).decode()
    check = input('Would you like to see the files that have been saved to the server? (Y/N)')
    if check.lower() == 'y':
        print('\nFiles saved To Server:')
        print(sent_filenames)


def list_files():
    current_directory = os.getcwd()
    files = [f for f in os.listdir(current_directory) if os.path.isfile(f)]
    return files


def save_file(data: bytes, file_path: str):
    with open(file_path, 'wb') as file:
        file.write(data)