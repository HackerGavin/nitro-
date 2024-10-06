import requests
import random
import string
import threading
import time
import sys

class CodeGenerator:
    def __init__(self):
        self.valid_codes = []
        self.invalid_count = 0
        self.valid_count = 0
        self.lock = threading.Lock()
        self.running = True

    def generate_code(self, length=19):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def check_code_validity(self, code):
        url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def process_code(self):
        while self.running:
            generated_code = self.generate_code()
            full_code = f"https://discord.gift/{generated_code}"

            if self.check_code_validity(generated_code):
                with self.lock:
                    self.valid_codes.append(full_code)
                    self.valid_count += 1
            else:
                with self.lock:
                    self.invalid_count += 1

    def display_counts(self):
        while self.running:
            with self.lock:
                # Use flush to force the print to update immediately
                print(f"\rValid codes: {self.valid_count} | Invalid codes: {self.invalid_count}", end="", flush=True)
            time.sleep(0.2)  # Update every 0.2 seconds

    def start(self, num_threads):
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=self.process_code)
            thread.start()
            threads.append(thread)

        display_thread = threading.Thread(target=self.display_counts)
        display_thread.start()

        for thread in threads:
            thread.join()

if __name__ == "__main__":
    num_threads = int(input("Enter the number of threads to run: "))
    code_gen = CodeGenerator()
    
    try:
        print("Starting code generation...")
        code_gen.start(num_threads)
    except KeyboardInterrupt:
        code_gen.running = False
        print("\nStopping code generation...")
