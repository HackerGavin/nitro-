import requests
import random
import string
import threading
import time
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Global variables for counting codes
valid_count = 0
invalid_count = 0
valid_codes_list = []
lock = threading.Lock()

def generate_code(length=19):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def check_code_validity(code):
    """Check if the generated code is valid using Discord's API."""
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    response = requests.get(url)
    return response.status_code == 200

def send_to_webhook(webhook_url, message):
    """Send a message to the specified Discord webhook."""
    data = {
        "content": message
    }
    requests.post(webhook_url, json=data)

def worker(num_codes, webhook_url):
    """Thread worker function to generate and check codes."""
    global valid_count, invalid_count
    total_codes_processed = 0

    for _ in range(num_codes):
        generated_code = generate_code()
        if check_code_validity(generated_code):
            valid_code_link = f"https://discord.gift/{generated_code}"
            update_counts(1, 0, valid_code_link)  # Save the valid code
            send_to_webhook(webhook_url, valid_code_link)  # Send valid code to webhook
        else:
            update_counts(0, 1)

        total_codes_processed += 1

        # Send a status update every 100,000 codes processed
        if total_codes_processed % 100000 == 0:
            with lock:
                send_to_webhook(webhook_url, f"@everyone Invalid Codes: {invalid_count} | Valid Codes: {valid_count}")

def update_counts(valid, invalid, code=None):
    """Update global counts in a thread-safe manner."""
    global valid_count, invalid_count
    with lock:
        valid_count += valid
        invalid_count += invalid
        if valid and code:
            valid_codes_list.append(code)

def status_report():
    """Print the status report every second."""
    while True:
        with lock:
            print(f"\r{Fore.LIGHTYELLOW_EX}Invalid Codes: {Fore.RED}{invalid_count} {Fore.LIGHTYELLOW_EX}| Valid Codes: {Fore.GREEN}{valid_count}    {Style.RESET_ALL}", end="")
        time.sleep(1)

def main(num_codes, num_threads, webhook_url):
    """Generate and check validity of gift codes with threading."""
    codes_per_thread = num_codes // num_threads
    threads = []

    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(codes_per_thread, webhook_url))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Slight delay to prevent overwhelming the API

    for thread in threads:
        thread.join()

    # Notify user of results
    with lock:
        if valid_count > 0:
            print(f"\n{Fore.LIGHTYELLOW_EX}Valid codes have been generated. You can view them using the command below.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}No valid codes found.{Style.RESET_ALL}")

def view_valid_codes():
    """Display valid codes when requested."""
    with lock:
        if valid_count > 0:
            print(f"{Fore.LIGHTYELLOW_EX}Here are the valid codes:{Style.RESET_ALL}")
            for code in valid_codes_list:
                print(f"{Fore.GREEN}{code}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No valid codes have been found.{Style.RESET_ALL}")

def check_for_view_input():
    """Check for user input to view valid codes."""
    while True:
        user_input = input()  # Wait for input from the user
        if user_input.lower() == 'v':
            view_valid_codes()

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}███╗░░░███╗░█████╗░██████╗░███████╗  ██████╗░██╗░░░██╗  ███████╗░█████╗░░██████╗████████╗██╗██╗░░██╗")
    print(f"{Fore.MAGENTA}████╗░████║██╔══██╗██╔══██╗██╔════╝  ██╔══██╗╚██╗░██╔╝  ╚════██║██╔══██╗██╔════╝╚══██╔══╝██║╚██╗██╔╝")
    print(f"{Fore.MAGENTA}██╔████╔██║███████║██║░░██║█████╗░░  ██████╦╝░╚████╔╝░  ░░███╔═╝███████║╚█████╗░░░░██║░░░██║░╚███╔╝░")
    print(f"{Fore.MAGENTA}██║╚██╔╝██║██╔══██║██║░░██║██╔══╝░░  ██╔══██╗░░╚██╔╝░░  ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██║░██╔██╗░")
    print(f"{Fore.MAGENTA}██║░╚═╝░██║██║░░██║██████╔╝███████╗  ██████╦╝░░░██║░░░  ███████╗██║░░██║██████╔╝░░░██║░░░██║██╔╝╚██╗")
    print(f"{Fore.MAGENTA}╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝  ╚═════╝░░░░╚═╝░░░  ╚══════╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝╚═╝░░╚═╝")

    webhook_url = input(f"{Fore.LIGHTYELLOW_EX}Enter your Discord webhook URL: {Style.RESET_ALL}")

    try:
        num_codes_to_generate = int(input(f"{Fore.LIGHTYELLOW_EX}Enter the number of codes to generate: {Style.RESET_ALL}"))
        if num_codes_to_generate < 1:
            print(f"{Fore.RED}Please enter a positive integer.{Style.RESET_ALL}")
        else:
            num_threads = min(100, num_codes_to_generate)  # Adjust max threads
            codes_per_thread = num_codes_to_generate // num_threads
            print(f"{Fore.LIGHTYELLOW_EX}Generating codes...{Style.RESET_ALL}")

            # Start the status report and input check threads
            threading.Thread(target=status_report, daemon=True).start()
            threading.Thread(target=check_for_view_input, daemon=True).start()
            main(num_codes_to_generate, num_threads, webhook_url)

            # Wait for threads to complete
            while threading.active_count() > 1:
                time.sleep(1)

    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
