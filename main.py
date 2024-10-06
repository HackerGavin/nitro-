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

def update_counts(valid, invalid):
    """Update global counts in a thread-safe manner."""
    global valid_count, invalid_count
    with lock:
        valid_count += valid
        invalid_count += invalid

def status_report():
    """Print the status report every 5 minutes."""
    while True:
        time.sleep(300)  # Wait for 5 minutes
        with lock:
            print(f"{Fore.YELLOW}Invalid Codes: {Fore.RED}{invalid_count} {Fore.YELLOW}| Valid Codes: {Fore.GREEN}{valid_count}")

def main(num_codes):
    """Generate and check validity of gift codes."""
    global valid_count, invalid_count

    for _ in range(num_codes):
        generated_code = generate_code()
        if check_code_validity(generated_code):
            update_counts(1, 0)  # Increment valid count
        else:
            update_counts(0, 1)  # Increment invalid count

    # Print all valid codes at once
    if valid_count > 0:
        print("Valid codes:")
        for i in range(valid_count):
            print(f"https://discord.gift/{generate_code()}")  # Replace with actual valid codes if desired
    else:
        print(f"{Fore.RED}No valid codes found.{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}███╗░░░███╗░█████╗░██████╗░███████╗  ██████╗░██╗░░░██╗  ███████╗░█████╗░░██████╗████████╗██╗██╗░░██╗")
    print(f"{Fore.MAGENTA}████╗░████║██╔══██╗██╔══██╗██╔════╝  ██╔══██╗╚██╗░██╔╝  ╚════██║██╔══██╗██╔════╝╚══██╔══╝██║╚██╗██╔╝")
    print(f"{Fore.MAGENTA}██╔████╔██║███████║██║░░██║█████╗░░  ██████╦╝░╚████╔╝░  ░░███╔═╝███████║╚█████╗░░░░██║░░░██║░╚███╔╝░")
    print(f"{Fore.MAGENTA}██║╚██╔╝██║██╔══██║██║░░██║██╔══╝░░  ██╔══██╗░░╚██╔╝░░  ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██║░██╔██╗░")
    print(f"{Fore.MAGENTA}██║░╚═╝░██║██║░░██║██████╔╝███████╗  ██████╦╝░░░██║░░░  ███████╗██║░░██║██████╔╝░░░██║░░░██║██╔╝╚██╗")
    print(f"{Fore.MAGENTA}╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝  ╚═════╝░░░░╚═╝░░░  ╚══════╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝╚═╝░░╚═╝")

    try:
        num_codes_to_generate = int(input(f"{Fore.GREEN}Enter the number of codes to generate: {Style.RESET_ALL}"))
        if num_codes_to_generate < 1:
            print("Please enter a positive integer.")
        else:
            print(f"{Fore.YELLOW}Generating codes...{Style.RESET_ALL}")

            # Start the status report thread
            threading.Thread(target=status_report, daemon=True).start()
            main(num_codes_to_generate)

    except ValueError:
        print("Invalid input. Please enter a number.")
