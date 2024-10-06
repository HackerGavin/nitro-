import asyncio
import random
import string
import time
from aiohttp import ClientSession
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Global variables for counting codes
valid_count = 0
invalid_count = 0
valid_codes_list = []
lock = asyncio.Lock()

async def generate_code(length=19):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def check_code_validity(session, code):
    """Check if the generated code is valid using Discord's API."""
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    async with session.get(url) as response:
        return response.status == 200

async def worker(num_codes, session):
    """Asynchronous worker to generate and check codes."""
    global valid_count, invalid_count
    for _ in range(num_codes):
        generated_code = await generate_code()
        if await check_code_validity(session, generated_code):
            async with lock:
                valid_count += 1
                valid_codes_list.append(f"https://discord.gift/{generated_code}")
        else:
            async with lock:
                invalid_count += 1

async def status_report():
    """Print the status report every second."""
    while True:
        await asyncio.sleep(1)
        async with lock:
            print(f"\r{Fore.LIGHTYELLOW_EX}Invalid Codes: {Fore.RED}{invalid_count} {Fore.LIGHTYELLOW_EX}| Valid Codes: {Fore.GREEN}{valid_count}    {Style.RESET_ALL}", end="")

async def main(num_codes, num_threads):
    """Generate and check validity of gift codes with asyncio."""
    codes_per_thread = num_codes // num_threads
    async with ClientSession() as session:
        tasks = [worker(codes_per_thread, session) for _ in range(num_threads)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}███╗░░░███╗░█████╗░██████╗░███████╗  ██████╗░██╗░░░██╗  ███████╗░█████╗░░██████╗████████╗██╗██╗░░██╗")
    print(f"{Fore.MAGENTA}████╗░████║██╔══██╗██╔══██╗██╔════╝  ██╔══██╗╚██╗░██╔╝  ╚════██║██╔══██╗██╔════╝╚══██╔══╝██║╚██╗██╔╝")
    print(f"{Fore.MAGENTA}██╔████╔██║███████║██║░░██║█████╗░░  ██████╦╝░╚████╔╝░  ░░███╔═╝███████║╚█████╗░░░░██║░░░██║░╚███╔╝░")
    print(f"{Fore.MAGENTA}██║╚██╔╝██║██╔══██║██║░░██║██╔══╝░░  ██╔══██╗░░╚██╔╝░░  ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██║░██╔██╗░")
    print(f"{Fore.MAGENTA}██║░╚═╝░██║██║░░██║██████╔╝███████╗  ██████╦╝░░░██║░░░  ███████╗██║░░██║██████╔╝░░░██║░░░██║██╔╝╚██╗")
    print(f"{Fore.MAGENTA}╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝  ╚═════╝░░░░╚═╝░░░  ╚══════╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝╚═╝░░╚═╝")

    try:
        num_codes_to_generate = int(input(f"{Fore.LIGHTYELLOW_EX}Enter the number of codes to generate: {Style.RESET_ALL}"))
        if num_codes_to_generate < 1:
            print(f"{Fore.RED}Please enter a positive integer.{Style.RESET_ALL}")
        else:
            num_threads = min(100, num_codes_to_generate)  # Increase the number of threads
            print(f"{Fore.LIGHTYELLOW_EX}Generating codes...{Style.RESET_ALL}")

            # Start the status report
            asyncio.run(status_report())
            asyncio.run(main(num_codes_to_generate, num_threads))

            # Print results
            async with lock:
                if valid_count > 0:
                    print(f"\n{Fore.LIGHTYELLOW_EX}Valid codes have been generated. You can view them using the command below.{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}No valid codes found.{Style.RESET_ALL}")

    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
