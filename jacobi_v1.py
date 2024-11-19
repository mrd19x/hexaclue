import random
import os
from bit import Key
import time

# Jacobi symbol calculation (used for checking quadratic residues)
def jacobi_symbol(a, n):
    """Compute the Jacobi symbol (a/n)"""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = a % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 == 3 or n % 8 == 5:
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    if n == 1:
        return result
    return 0  # if n is not a prime

def generate_random_key():
    """Generate a random 64-byte hex string as a private key"""
    return f"{random.getrandbits(256):064x}"

def clear_console():
    """Clear the console for a fresh start"""
    os.system('cls' if os.name == 'nt' else 'clear')

def find_address_with_random_search(start_hex, end_hex, target_address, enable_log=True):
    """Find a Bitcoin address through random key generation and Jacobi checking."""
    start_int = int(start_hex, 16)
    end_int = int(end_hex, 16)
    
    # Define a range for random search
    search_range = end_int - start_int + 1

    print(f"Starting random search from {start_hex} to {end_hex} for address {target_address}")

    processed_keys = 0  # To keep track of how many keys we've processed
    
    while True:
        # Generate a random key in the range
        random_int = random.randint(start_int, end_int)
        random_hex = f"{random_int:064x}"
        
        try:
            key = Key.from_hex(random_hex)
            address = key.address

            if enable_log:
                # Log hex and address when enable_log is True
                print(f"Hex: {random_hex} | Address: {address}")
            
            # Check if this address matches the target address
            if address == target_address:
                print(f"Success! Found matching private key: {random_hex}")
                with open(f"{target_address}.txt", "w") as file:
                    file.write(random_hex)
                print(f"Private key saved to {target_address}.txt")
                break
        except Exception as e:
            continue  # Skip if error occurs (invalid key, etc.)
        
        # Apply Jacobi symbol to check some property
        jacobi_result = jacobi_symbol(random_int, 101)  # Example with prime n = 101
        if jacobi_result == 1:  # Example condition
            pass  # Continue searching if Jacobi condition is met
        
        # Update processed keys count
        processed_keys += 1
        
        if not enable_log:
            # If logging is off, print the current progress in a dynamic, single-line format
            print(f"\rProcessed {processed_keys} keys... - Current Hex: {random_hex} - Address: {address}", end="")
            # time.sleep(0.1)  # Slight delay to ensure the update is visible and smooth

def main():
    start_hex = input("Enter start hexadecimal: ")
    end_hex = input("Enter end hexadecimal: ")
    target_address = input("Enter target Bitcoin address: ")
    enable_log = input("Enable log (True/False): ").strip().lower() == 'true'  # Convert to boolean
    
    # Clear console before starting the search
    clear_console()
    
    find_address_with_random_search(start_hex, end_hex, target_address, enable_log)

if __name__ == "__main__":
    main()
