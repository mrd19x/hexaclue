#!/bin/bash

# Meminta input pengguna
read -p "Masukkan nilai hexa: " hexa
read -p "Masukkan alamat: " address
read -p "Berapa banyak sesi screen yang ingin dibuka? " jumlah

echo "Menjalankan aplikasi Python dengan hexa=$hexa dan address=$address"

# Loop untuk membuka sesi screen
for ((i=1; i<=jumlah; i++))
do
    # Membuka sesi screen baru dan menjalankan script Python dengan argumen yang sesuai
    screen -dmS "session_$i" bash -c "python3 app.py --hexclue \"$hexa\" --address \"$address\" --save; exec bash"
done

echo "Selesai membuka $jumlah sesi screen."
