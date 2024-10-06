import random
import string
import aiohttp
import asyncio
import time
import threading
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Global variables for counting codes
valid_count = 0
invalid_count = 0
valid_codes_list = []
lock = threading.Lock()

async def check_code_validity(session, code):
    """Check if the generated code is valid using Discord's API."""
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    try:
        async with session.get(url) as response:
            return response.status == 200
    except Exception as e:
        print(f"{Fore.RED}Error checking code {code}: {e}{Style.RESET_ALL}")
        return False

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
                await update_counts(1, 0, valid_code_link)
            else:
                await update_counts(0, 1)

            total_codes_processed += 1

            # Automatically trigger update every 10,000 codes processed
            if total_codes_processed % 10000 == 0:
                await auto_trigger_update(webhook_url)

async def update_counts(valid, invalid, code=None):
    """Update global counts in a thread-safe manner."""
    global valid_count, invalid_count
    with lock:
        valid_count += valid
        invalid_count += invalid
        if valid and code:
            valid_codes_list.append(code)

async def send_to_webhook(webhook_url, message):
    """Send a message to the specified Discord webhook."""
    data = {
        "content": message
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=data) as response:
                if response.status != 204:
                    print(f"{Fore.RED}Failed to send message to webhook: {response.status} {await response.text()}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}Message sent to webhook successfully.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error sending to webhook: {e}{Style.RESET_ALL}")

async def send_status_update(webhook_url):
    """Send a status update to the webhook."""
    with lock:
        valid_codes_message = "\n".join(valid_codes_list) if valid_codes_list else "No valid codes found."
        message = (
            f"@everyone\n"
            f"Invalid Codes: {invalid_count}\n"
            f"Valid Codes: {valid_count}\n"
            f"Valid Code Links:\n{valid_codes_message}"
        )
        await send_to_webhook(webhook_url, message)

async def auto_trigger_update(webhook_url):
    """Automatically trigger an update when reaching 10,000 codes."""
    await send_status_update(webhook_url)

async def check_for_user_input(webhook_url):
    """Check for user input to trigger webhook manually."""
    while True:
        user_input = input()
        if user_input.lower() == "codes":
            await auto_trigger_update(webhook_url)

def status_report():
    """Print the status report every second."""
    while True:
        with lock:
            print(f"\r{Fore.LIGHTYELLOW_EX}Invalid Codes: {Fore.RED}{invalid_count} {Fore.LIGHTYELLOW_EX}| Valid Codes: {Fore.GREEN}{valid_count}    {Style.RESET_ALL}", end="")
        time.sleep(1)

async def main(total_codes, webhook_url):
    """Generate and check validity of gift codes."""
    num_workers = min(100, total_codes)
    codes_per_worker = total_codes // num_workers

    # Start worker tasks
    tasks = [worker(codes_per_worker, webhook_url) for _ in range(num_workers)]
    await asyncio.gather(*tasks)

    with lock:
        if valid_count > 0:
            print(f"\n{Fore.LIGHTYELLOW_EX}Valid codes have been generated. You can view them using the command below.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}No valid codes found.{Style.RESET_ALL}")

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

            # Start the status report in a separate thread
            threading.Thread(target=status_report, daemon=True).start()

            # Start user input listener and main code generation concurrently
            asyncio.run(check_for_user_input(webhook_url))
            asyncio.run(main(total_codes_to_generate, webhook_url))

    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
