import requests
import random
import string
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

valid_codes = []
invalid_count = 0
valid_count = 0
lock = threading.Lock()

def generate_code(length=19):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def check_code_validity(code):
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def process_code():
    global valid_count, invalid_count
    generated_code = generate_code()
    full_code = f"https://discord.gift/{generated_code}"

    if check_code_validity(generated_code):
        with lock:
            valid_codes.append(full_code)
            valid_count += 1
    else:
        with lock:
            invalid_count += 1

def display_counts():
    while True:
        with lock:
            print(f"\rValid codes: {valid_count} | Invalid codes: {invalid_count}", end="")
        time.sleep(0.2)  # Update every 0.2 seconds

def main(num_codes):
    # Start the display thread
    display_thread = threading.Thread(target=display_counts)
    display_thread.daemon = True
    display_thread.start()

    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(process_code) for _ in range(num_codes)]
        for future in as_completed(futures):
            future.result()  # This can also be used to handle exceptions if necessary

if __name__ == "__main__":
    num_codes_to_generate = int(input("Enter the number of codes to generate: "))
    main(num_codes_to_generate)
