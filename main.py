import requests
import random
import string

def generate_code(length=19):
    """Generate a random code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def check_code_validity(code):
    """Check if the generated code is valid using Discord's API."""
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    response = requests.get(url)
    return response.status_code == 200

def main(num_codes):
    """Generate and check validity of gift codes."""
    valid_codes = []
    
    for _ in range(num_codes):
        generated_code = generate_code()
        full_code = f"https://discord.gift/{generated_code}"
        
        if check_code_validity(generated_code):
            valid_codes.append(full_code)

    # Print all valid codes at once
    if valid_codes:
        print("Valid codes:")
        for code in valid_codes:
            print(code)
    else:
        print("No valid codes found.")

if __name__ == "__main__":
    print("███╗░░░███╗░█████╗░██████╗░███████╗  ██████╗░██╗░░░██╗  ███████╗░█████╗░░██████╗████████╗██╗██╗░░██╗")
    print("████╗░████║██╔══██╗██╔══██╗██╔════╝  ██╔══██╗╚██╗░██╔╝  ╚════██║██╔══██╗██╔════╝╚══██╔══╝██║╚██╗██╔╝")
    print("██╔████╔██║███████║██║░░██║█████╗░░  ██████╦╝░╚████╔╝░  ░░███╔═╝███████║╚█████╗░░░░██║░░░██║░╚███╔╝░")
    print("██║╚██╔╝██║██╔══██║██║░░██║██╔══╝░░  ██╔══██╗░░╚██╔╝░░  ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██║░██╔██╗░")
    print("██║░╚═╝░██║██║░░██║██████╔╝███████╗  ██████╦╝░░░██║░░░  ███████╗██║░░██║██████╔╝░░░██║░░░██║██╔╝╚██╗")
    print("╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝  ╚═════╝░░░░╚═╝░░░  ╚══════╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝╚═╝░░╚═╝")

    try:
        num_codes_to_generate = int(input("Enter the number of codes to generate: "))
        if num_codes_to_generate < 1:
            print("Please enter a positive integer.")
        else:
            main(num_codes_to_generate)
    except ValueError:
        print("Invalid input. Please enter a number.")
