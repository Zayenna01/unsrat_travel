# UNSRAT Travel Analytics - Apriori

Aplikasi web Data Mining untuk menganalisis pola kota wisata pada 8 paket Travel UNSRAT menggunakan algoritma Apriori.

## Fitur
- Dataset 8 paket wisata dari soal.
- Parameter minimum support dan minimum confidence dapat diubah.
- Menampilkan kandidat C1, C2, ... dan frequent itemset L1, L2, ...
- Menghasilkan association rules yang memenuhi minimum confidence.
- Rekomendasi kombinasi kota dengan frequent itemset terbesar.
- Ekspor hasil frequent itemset dan association rules ke CSV.

## Persyaratan
- Python 3.9 atau lebih baru
- pip

## Cara menjalankan di Windows

1. Ekstrak folder `unsrat_apriori_web`.
2. Buka Command Prompt atau terminal pada folder tersebut.
3. Buat virtual environment (opsional tetapi disarankan):

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install Flask:

   ```bash
   pip install -r requirements.txt
   ```

5. Jalankan aplikasi:

   ```bash
   python app.py
   ```

6. Buka browser dan kunjungi:

   `http://127.0.0.1:5000`

## Cara kerja
1. Sistem membaca delapan transaksi paket wisata yang sudah dimasukkan pada `app.py`.
2. Pengguna mengisi minimum support dan minimum confidence dalam persen.
3. Sistem mengubah parameter persen menjadi desimal.
4. Sistem menghitung minimum support count dengan pembulatan ke atas.
5. Sistem membentuk kandidat itemset, menyaring frequent itemset, lalu membangkitkan association rules.
6. Hasil ditampilkan pada halaman web dan dapat diekspor ke CSV.

## Catatan metodologi
Support = jumlah transaksi yang memuat itemset / jumlah seluruh transaksi.

Confidence(A -> B) = support count(A gabungan B) / support count(A).

Minimum support count menggunakan ceiling(minimum support x jumlah transaksi). Dengan 8 transaksi dan minimum support 30%, nilai minimumnya adalah 3 transaksi.

Aplikasi memakai implementasi Apriori sendiri (tanpa library pihak ketiga) agar tahapan kandidat dan frequent itemset dapat ditampilkan untuk keperluan pembelajaran.
