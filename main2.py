import requests
import random
import string
from concurrent.futures import ThreadPoolExecutor
import threading
import time

valid_codes = []
invalid_count = 0
valid_count = 0
lock = threading.Lock()

def generate_code(length=19):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

def check_code_validity(code):
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False

def process_code(_):
    global valid_count, invalid_count
    generated_code = generate_code()
    full_code = f"https://discord.gift/{generated_code}"
    
    is_valid = check_code_validity(generated_code)
    
    with lock:
        if is_valid:
            valid_codes.append(full_code)
            valid_count += 1
            return f"Valid code: {full_code}"
        else:
            invalid_count += 1
            return None  # Avoid spamming invalid links

def display_counts():
    while True:
        with lock:
            print(f"\rValid codes: {valid_count} | Invalid codes: {invalid_count}", end="")
        time.sleep(1)

def main(num_codes):
    display_thread = threading.Thread(target=display_counts)
    display_thread.daemon = True
    display_thread.start()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_code, range(num_codes))
    
    # Wait for the user to input 'v'
    while True:
        user_input = input("\nPress 'v' to view valid codes or 'q' to quit: ").strip().lower()
        if user_input == 'v':
            with lock:
                if valid_codes:
                    print("Valid codes found:")
                    for code in valid_codes:
                        print(code)
                else:
                    print("No valid codes yet.")
        elif user_input == 'q':
            break

if __name__ == "__main__":
    num_codes_to_generate = int(input("Enter the number of codes to generate: "))
    main(num_codes_to_generate)
