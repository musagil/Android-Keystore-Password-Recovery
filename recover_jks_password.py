import itertools
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_password(keystore_path, password):
    command = ['keytool', '-list', '-keystore', keystore_path, '-storepass', password]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output, _ = process.communicate()
    if process.returncode == 0:
        return password  # Return the password when found
    return None  # Return None if the password is not found

def recover_jks_password(keystore_path, dictionary_path, max_words, num_threads=4):
    with open(dictionary_path, 'r') as dictionary_file:
        words = dictionary_file.read().splitlines()

    # Calculate the total number of combinations
    total_combinations = sum(len(list(itertools.permutations(words, length))) for length in range(1, max_words + 1))

    progress = 0  # Initialize progress

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for length in range(1, max_words + 1):
            combinations = itertools.permutations(words, length)
            futures = [executor.submit(check_password, keystore_path, ''.join(combination)) for combination in combinations]
            for future in as_completed(futures):
                progress += 1
                if future.result() is not None:
                    password = future.result()
                    print(f"Password found: {password}")
                    return
                else:
                    # Calculate and print the progress percentage
                    percentage = (progress / total_combinations) * 100
                    print(f"Progress: {percentage:.2f}%")

    print("Password not found.")

# Usage example
keystore_path = 'YOUR KEYSTORE PATH'
dictionary_path = 'A DICTIONARY PATH, words should separated by newlines'
max_words = 3
num_threads = 8
recover_jks_password(keystore_path, dictionary_path, max_words, num_threads)
