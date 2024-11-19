import random
import os
from bit import Key
import time
import multiprocessing
from multiprocessing import Manager

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

def search_random_keys(start_int, end_int, target_address, manager_dict, processed_keys, enable_log):
    """Search for matching Bitcoin addresses in a parallelized manner."""
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
                manager_dict['found'] = True
                break
        except Exception as e:
            continue  # Skip if error occurs (invalid key, etc.)
        
        # Apply Jacobi symbol to check some property
        jacobi_result = jacobi_symbol(random_int, 101)  # Example with prime n = 101
        if jacobi_result == 1:  # Example condition
            pass  # Continue searching if Jacobi condition is met
        
        # Update processed keys count
        processed_keys.value += 1
        
        if not enable_log:
            # If logging is off, print the current progress in a dynamic, single-line format
            print(f"\rProcessed {processed_keys.value} keys... - Current Hex: {random_hex} - Address: {address}", end="")

def find_address_with_random_search(start_hex, end_hex, target_address, enable_log=True, num_workers=4):
    """Find a Bitcoin address through random key generation and Jacobi checking."""
    start_int = int(start_hex, 16)
    end_int = int(end_hex, 16)

    # Define a range for random search
    search_range = end_int - start_int + 1

    print(f"Starting random search from {start_hex} to {end_hex} for address {target_address}")

    # Create a manager for shared state between processes
    manager = Manager()
    manager_dict = manager.dict()
    manager_dict['found'] = False
    processed_keys = manager.Value('i', 0)  # To keep track of processed keys count
    
    # Split the range for parallel processing
    step = search_range // num_workers
    ranges = [(start_int + i * step, start_int + (i + 1) * step - 1) for i in range(num_workers)]
    
    processes = []
    for r in ranges:
        p = multiprocessing.Process(target=search_random_keys, args=(r[0], r[1], target_address, manager_dict, processed_keys, enable_log))
        processes.append(p)
        p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()

    if not manager_dict['found']:
        print(f"Address not found in the range {start_hex} to {end_hex}.")
        
    print(f"Total processed keys: {processed_keys.value}")

def main():
    start_hex = input("Enter start hexadecimal: ")
    end_hex = input("Enter end hexadecimal: ")
    target_address = input("Enter target Bitcoin address: ")
    enable_log = input("Enable log (True/False): ").strip().lower() == 'true'  # Convert to boolean
    
    # Clear console before starting the search
    clear_console()
    
    # Set number of workers based on CPU cores or a fixed value
    num_workers = multiprocessing.cpu_count()

    find_address_with_random_search(start_hex, end_hex, target_address, enable_log, num_workers)

if __name__ == "__main__":
    main()
