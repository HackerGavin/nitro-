import random
import string
import aiohttp
import asyncio
import time
import threading  # Importing threading
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Global variables for counting codes
valid_count = 0
invalid_count = 0
valid_codes_list = []
lock = threading.Lock()  # Use threading.Lock for the status report

async def check_code_validity(session, code):
    """Check if the generated code is valid using Discord's API."""
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    async with session.get(url) as response:
        return response.status == 200

def generate_code(length=19):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def worker(codes_to_generate, webhook_url):
    """Worker function to generate and check codes."""
    global valid_count, invalid_count
    total_codes_processed = 0

    async with aiohttp.ClientSession() as session:
        for _ in range(codes_to_generate):
            generated_code = generate_code()
            if await check_code_validity(session, generated_code):
                valid_code_link = f"https://discord.gift/{generated_code}"
                await update_counts(1, 0, valid_code_link)  # Save the valid code
            else:
                await update_counts(0, 1)

            total_codes_processed += 1

            # Send a status update every 10,000 codes processed
            if total_codes_processed % 10000 == 0:
                await send_status_update(webhook_url)

async def update_counts(valid, invalid, code=None):
    """Update global counts in a thread-safe manner."""
    global valid_count, invalid_count
    async with lock:  # This remains an asyncio lock
        valid_count += valid
        invalid_count += invalid
        if valid and code:
            valid_codes_list.append(code)

async def send_to_webhook(webhook_url, message):
    """Send a message to the specified Discord webhook."""
    data = {
        "content": message
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=data) as response:
            if response.status != 204:
                print(f"{Fore.RED}Failed to send message to webhook: {response.status} {await response.text()}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Message sent to webhook successfully.{Style.RESET_ALL}")

async def send_status_update(webhook_url):
    """Send a status update to the webhook."""
    async with lock:
        valid_codes_message = "\n".join(valid_codes_list) if valid_codes_list else "No valid codes found."

        message = (
            f"@everyone\n"
            f"Invalid Codes: {invalid_count}\n"
            f"Valid Codes: {valid_count}\n"
            f"Valid Code Links:\n{valid_codes_message}"
        )
        await send_to_webhook(webhook_url, message)

async def main(total_codes, webhook_url):
    """Generate and check validity of gift codes."""
    # Create workers
    tasks = []
    num_workers = min(100, total_codes)  # Set max workers
    codes_per_worker = total_codes // num_workers

    for _ in range(num_workers):
        tasks.append(worker(codes_per_worker, webhook_url))

    await asyncio.gather(*tasks)

    # Final notification
    async with lock:
        if valid_count > 0:
            print(f"\n{Fore.LIGHTYELLOW_EX}Valid codes have been generated. You can view them using the command below.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}No valid codes found.{Style.RESET_ALL}")

def status_report():
    """Print the status report every second."""
    while True:
        with lock:  # Using threading.Lock here
            print(f"\r{Fore.LIGHTYELLOW_EX}Invalid Codes: {Fore.RED}{invalid_count} {Fore.LIGHTYELLOW_EX}| Valid Codes: {Fore.GREEN}{valid_count}    {Style.RESET_ALL}", end="")
        time.sleep(1)

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}███╗░░░███╗░█████╗░██████╗░███████╗  ██████╗░██╗░░░██╗  ███████╗░█████╗░░██████╗████████╗██╗██╗░░██╗")
    print(f"{Fore.MAGENTA}████╗░████║██╔══██╗██╔══██╗██╔════╝  ██╔══██╗╚██╗░██╔╝  ╚════██║██╔══██╗██╔════╝╚══██╔══╝██║╚██╗██╔╝")
    print(f"{Fore.MAGENTA}██╔████╔██║███████║██║░░██║█████╗░░  ██████╦╝░╚████╔╝░  ░░███╔═╝███████║╚█████╗░░░░██║░░░██║░╚███╔╝░")
    print(f"{Fore.MAGENTA}██║╚██╔╝██║██╔══██║██║░░██║██╔══╝░░  ██╔══██╗░░╚██╔╝░░  ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██║░██╔██╗░")
    print(f"{Fore.MAGENTA}██║░╚═╝░██║██║░░██║██████╔╝███████╗  ██████╦╝░░░██║░░░  ███████╗██║░░██║██████╔╝░░░██║░░░██║██╔╝╚██╗")
    print(f"{Fore.MAGENTA}╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝  ╚═════╝░░░░╚═╝░░░  ╚══════╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝╚═╝░░╚═╝")

    webhook_url = input(f"{Fore.LIGHTYELLOW_EX}Enter your Discord webhook URL: {Style.RESET_ALL}")

    try:
        total_codes_to_generate = int(input(f"{Fore.LIGHTYELLOW_EX}Enter the total number of codes to generate: {Style.RESET_ALL}"))
        if total_codes_to_generate < 1:
            print(f"{Fore.RED}Please enter a positive integer.{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTYELLOW_EX}Generating codes...{Style.RESET_ALL}")

            # Start the status report in the background
            threading.Thread(target=status_report, daemon=True).start()

            # Run the main async function
            asyncio.run(main(total_codes_to_generate, webhook_url))

    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
