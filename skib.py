import random
import string
import asyncio
import aiohttp

async def generate_code(length=19):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def check_code_validity(session, code):
    url = f"https://discord.com/api/v8/entitlements/gift-codes/{code}"
    async with session.get(url) as response:
        return response.status == 200

async def main(num_codes):
    valid_count = 0
    invalid_count = 0
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_codes):
            generated_code = await generate_code()
            full_code = f"https://discord.gift/{generated_code}"
            tasks.append((full_code, check_code_validity(session, generated_code)))

        results = await asyncio.gather(*[task[1] for task in tasks])
        
        for i, valid in enumerate(results):
            full_code = tasks[i][0]
            if valid:
                print(f"Valid code: {full_code}")
                valid_count += 1
            else:
                print(f"Invalid code: {full_code}")
                invalid_count += 1

    print(f"\nSummary:\nValid codes: {valid_count}\nInvalid codes: {invalid_count}")

if __name__ == "__main__":
    num_codes_to_generate = int(input("Enter the number of codes to generate: "))
    asyncio.run(main(num_codes_to_generate))
