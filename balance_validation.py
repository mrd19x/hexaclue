import os
import csv
import requests
import pandas as pd
import time
import argparse
from tqdm import tqdm  # Import tqdm untuk progress bar

# Lokasi output dan log file
output_file = "founds.csv"
log_file = "logs.txt"

def log_processed_file(filename):
    """Catat file yang telah diproses ke log."""
    with open(log_file, 'a') as log:
        log.write(f"{filename}\n")

def check_balance(addresses):
    """Cek balance dari blockchain.info untuk daftar alamat."""
    url = f"https://blockchain.info/balance?active={'|'.join(addresses)}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching balance: {e}")
        return {}

def process_file(file_path):
    """Proses file CSV, cek balance, dan simpan hasil jika ditemukan."""
    print(f"Processing file: {file_path}")
    found_addresses = []
    
    # Baca file CSV, selalu skip baris pertama
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Melewati baris pertama secara eksplisit
        rows = [{"Address": row[0], "Hex Address": row[1]} for row in reader]

    # Ambil hanya alamat dari setiap baris
    addresses = [row['Address'] for row in rows]

    # Proses dalam batch 250 alamat, tambahkan progress bar
    with tqdm(total=len(addresses), desc="Checking addresses", unit="address") as pbar:
        for i in range(0, len(addresses), 250):
            batch = addresses[i:i + 250]
            balance_data = check_balance(batch)
            
            # Tambahkan jeda 1,3 detik sebelum melanjutkan
            time.sleep(1.3)
            
            for address, data in balance_data.items():
                if data.get("final_balance", 0) > 0:
                    # Jika balance ditemukan, simpan detailnya
                    for row in rows:
                        if row['Address'] == address:
                            found_addresses.append({
                                "address": address,
                                "hexa": row["Hex Address"],
                                "balance": data["final_balance"]
                            })
            
            # Perbarui progress bar
            pbar.update(len(batch))

    # Simpan hasil jika ada alamat dengan balance
    if found_addresses:
        df = pd.DataFrame(found_addresses)
        if os.path.exists(output_file):
            df.to_csv(output_file, mode='a', header=False, index=False)
        else:
            df.to_csv(output_file, index=False)
    
    # Hapus file setelah selesai diproses
    os.remove(file_path)
    print(f"Completed processing: {file_path}")
    
    # Catat file ke log
    log_processed_file(file_path)

def main():
    # Parsing argument
    parser = argparse.ArgumentParser(description="Process Bitcoin address balance checks from CSV files.")
    parser.add_argument("--input_dir", required=True, help="Path to the directory containing CSV files.")
    args = parser.parse_args()
    
    input_dir = args.input_dir

    # Validasi input_dir
    if not os.path.isdir(input_dir):
        print(f"Error: The specified input_dir '{input_dir}' does not exist or is not a directory.")
        return
    
    # Iterasi melalui semua file dalam direktori
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_dir, filename)
            process_file(file_path)

if __name__ == "__main__":
    main()
