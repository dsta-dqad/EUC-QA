# End User Computing Quality Assurance DSTA

## Release Notes

### [v1.0.0] - 08/11/2024

#### Fitur Awal:

- Implementasi algoritma inti untuk EUC **SSKI**.
- Implementasi algoritma inti untuk EUC **SEKDA**.

#### ALGORITMA SSKI:

1. **Pemeriksaan Konsistensi**:

   - **Konsistensi Vertikal**: Memastikan konsistensi komponen terhadap komponen aggregatnya.
   - **Konsistensi Horizontal**: Memverifikasi konsistensi data antar periode waktu.
   - **Konsistensi Before-After**: Membandingkan tren data publikasi periode sebelum dan periode terbaru.

2. **Pemeriksaan Kewajaran**:
   - **Deteksi Pencilan**:
     - Menggunakan metode **Interquartile Range (IQR)** untuk mengidentifikasi anomali pada data komponen SSKI.
