import argparse
import secrets
import string
import os
import csv
from datetime import datetime
from bit import Key
from tqdm import tqdm

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def generate_btc_addresses(hexclue, num_results, progress_bar, target_address=None, buffer=None, addresses_count=0):
    for i in range(num_results):
        hex_address = ""
        for char in hexclue:
            if char == 'x':
                hex_address += secrets.choice(string.hexdigits.lower())
            else:
                hex_address += char
        try:
            key = Key.from_hex(hex_address)
            address = key.address
            buffer.append([address, hex_address])

            if target_address and address == target_address:
                save_to_file(address, hex_address)
                return True, addresses_count + 1

            addresses_count += 1

            if len(buffer) >= 1000000:
                save_buffer_to_csv(buffer)
                buffer.clear()

        except Exception as e:
            pass
        
        progress_bar.update(1)

    return False, addresses_count

def save_to_file(address, hex_address):
    os.makedirs('hexclue', exist_ok=True)
    filename = f"hexclue/{address}.txt"
    
    # Open the file in append mode ('a') so it doesn't overwrite the existing content
    with open(filename, mode='a') as file:
        file.write(f"Address: {address}\nHex: {hex_address}\n")

def save_buffer_to_csv(buffer):
    os.makedirs('hexclue', exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    csv_filename = f"hexclue/results_{timestamp}.csv"
    
    # Open the file in append mode ('a') so it doesn't overwrite the existing content
    with open(csv_filename, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        
        # Check if the file is empty (for adding headers to the file if it's new)
        file.seek(0, os.SEEK_END)
        if file.tell() == 0:
            # If the file is empty, write the header row
            csv_writer.writerow(['Address', 'Hex Address'])
        
        csv_writer.writerows(buffer)

def calculate_possible_results(hexclue):
    num_x = hexclue.count('x')
    if num_x == 0:
        return 0
    return 16 ** num_x

def main():
    parser = argparse.ArgumentParser(description="Generate Bitcoin addresses from a hex range.")
    parser.add_argument('--hexclue', type=str, required=True)
    parser.add_argument('--number_results', type=int, default=None)
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--address', type=str, default=None)
    
    args = parser.parse_args()
    
    clear_console()
    
    if args.number_results is None:
        possible_results = calculate_possible_results(args.hexclue)
        num_results = possible_results
    else:
        num_results = args.number_results
    
    buffer = []
    addresses_count = 0
    
    while True:
        progress_bar = tqdm(total=num_results, desc="Generating Bitcoin addresses", unit="address", position=0)

        found_address, addresses_count = generate_btc_addresses(args.hexclue, num_results, progress_bar, 
                                                                target_address=args.address, buffer=buffer, 
                                                                addresses_count=addresses_count)
        
        if args.address and found_address:
            break

        if args.address:
            pass

    if buffer:
        save_buffer_to_csv(buffer)

if __name__ == "__main__":
    main()
