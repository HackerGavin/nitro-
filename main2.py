import asyncio
import random
import string
import aiohttp
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Global variables for counting codes
valid_count = 0
invalid_count = 0
valid_codes_list = []

async def generate_code(length=19):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def check_code_validity(session, code):
    """Check if the generated code is valid using Discord's API."""
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    async with session.get(url) as response:
        return response.status == 200

async def update_counts(valid, code=None):
    """Update global counts."""
    global valid_count, invalid_count, valid_codes_list
    if valid:
        valid_count += 1
        valid_codes_list.append(f"https://discord.gift/{code}")
    else:
        invalid_count += 1

async def display_counts():
    """Display the counts of valid and invalid codes live."""
    while True:
        print(f"\rInvalid Codes: {Fore.RED}{invalid_count} | Valid Codes: {Fore.GREEN}{valid_count}", end="")
        await asyncio.sleep(1)  # Update every second

async def main(num_codes):
    """Generate and check validity of gift codes."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_codes):
            generated_code = await generate_code()
            tasks.append(check_code_validity(session, generated_code))

        results = await asyncio.gather(*tasks)

        for result, code in zip(results, [await generate_code() for _ in range(num_codes)]):
            await update_counts(result, code)

    # Final results
    print(f"\nFinal Results: Invalid Codes: {Fore.RED}{invalid_count} | Valid Codes: {Fore.GREEN}{valid_count}{Style.RESET_ALL}")
    if valid_count > 0:
        print(f"{Fore.LIGHTYELLOW_EX}Valid codes have been generated. You can view them using the command below.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No valid codes found.{Style.RESET_ALL}")

def view_valid_codes():
    """Display valid codes when requested."""
    if valid_count > 0:
        print(f"{Fore.LIGHTYELLOW_EX}Here are the valid codes:{Style.RESET_ALL}")
        for code in valid_codes_list:
            print(f"{Fore.GREEN}{code}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No valid codes have been found.{Style.RESET_ALL}")

async def check_for_view_input():
    """Check for user input to view valid codes."""
    while True:
        user_input = input()  # Wait for input from the user
        if user_input.lower() == 'v':
            view_valid_codes()

async def run(num_codes_to_generate):
    """Run the main code generation and input check."""
    await asyncio.gather(check_for_view_input(), display_counts(), main(num_codes_to_generate))

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Discord Code Generator (Optimized)")

    try:
        num_codes_to_generate = int(input(f"{Fore.LIGHTYELLOW_EX}Enter the number of codes to generate: {Style.RESET_ALL}"))
        if num_codes_to_generate < 1:
            print(f"{Fore.RED}Please enter a positive integer.{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTYELLOW_EX}Generating codes...{Style.RESET_ALL}")

            # Start displaying counts immediately after input
            asyncio.run(run(num_codes_to_generate))

    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
