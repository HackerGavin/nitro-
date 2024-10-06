import requests
import random
import string

def generate_code(length=19):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

def check_code_validity(code):
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    response = requests.get(url)
    return response.status_code == 200

def main(num_codes):
    for _ in range(num_codes):
        generated_code = generate_code()
        full_code = f"https://discord.gift/{generated_code}"
        
        if check_code_validity(generated_code):
            print(f"Valid code: {full_code}")
        else:
            print(f"Invalid code: {full_code}")

if __name__ == "__main__":
    num_codes_to_generate = int(input("Enter the number of codes to generate: "))
    main(num_codes_to_generate)
