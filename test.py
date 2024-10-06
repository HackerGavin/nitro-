import requests

def check_gift_link(link):
    response = requests.get(link)
    
    # Check for specific response codes
    if response.status_code == 200:
        return "Valid and not redeemed"
    elif response.status_code == 404:
        return "Invalid link (not found)"
    elif response.status_code == 403:
        return "Link has been redeemed or is invalid"
    else:
        return f"Unexpected status code: {response.status_code}"

def main():
    links = input("Paste your Discord gift links separated by commas: ").split(',')
    links = [link.strip() for link in links]  # Clean up any extra spaces

    results = {}
    for link in links:
        results[link] = check_gift_link(link)

    # Display results
    for link, result in results.items():
        print(f"{link}: {result}")

if __name__ == "__main__":
    main()
