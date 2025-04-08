import mysql.connector
import pandas as pd
from datetime import datetime

def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="zakat_db"
        )
    except mysql.connector.Error as e:
        print(f"Error: Gagal koneksi ke database - {str(e)}")
        exit(1)

def create_beras_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS beras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            harga DECIMAL(10,2)
        )
    ''')
    db.commit()

#beras db
def tambah_data_beras():
    db = connect_db()
    cursor = db.cursor()
    try:
        print("\n=== Tambah Data Beras ===")
        harga = float(input("Masukkan harga beras per Liter: Rp "))
        
        cursor.execute('''
            INSERT INTO beras (harga)
            VALUES (%s)
        ''', (harga,))
        db.commit()
        print("\nHarga beras berhasil ditambahkan!")
        
    except ValueError:
        print("Error: Harga harus berupa angka!")
    except Exception as e:
        print(f"Error: {str(e)}")

def tampilkan_data_beras():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM beras')
        hasil = cursor.fetchall()
        
        if not hasil:
            print("\nBelum ada data harga beras")
            return None
            
        print("\n=== Daftar Harga Beras ===")
        print("-" * 35)
        print(f"{'ID':^4} | {'Harga/Liter':^28}")
        print("-" * 35)
        
        for row in hasil:
            print(f"{row[0]:^4} | Rp {float(row[1]):>24,.2f}")
        print("-" * 35)
        return hasil
    except mysql.connector.Error as e:
        print(f"Error: Gagal mengambil data beras - {str(e)}")
        return None

# #pembayaran db
def create_payment_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pembayaran (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(100),
            jumlah_jiwa INT,
            jenis_zakat VARCHAR(10),
            metode_pembayaran VARCHAR(50),
            total_bayar DECIMAL(10,2),
            nominal_dibayar DECIMAL(10,2),
            kembalian DECIMAL(10,2),
            keterangan TEXT,
            tanggal_bayar DATETIME
        )
    ''')
    db.commit()

def tampilkan_data_pembayaran():
    db = connect_db()
    cursor = db.cursor()
    print("\n=== Data Pembayaran Zakat ===")
    cursor.execute("""
        SELECT nama, jumlah_jiwa, metode_pembayaran, 
               total_bayar, nominal_dibayar, kembalian, 
               tanggal_bayar 
        FROM pembayaran 
        ORDER BY tanggal_bayar DESC
    """)
    hasil = cursor.fetchall()
    
    if not hasil:
        print("Belum ada data pembayaran")
        return
        
    print("-" * 100)
    print(f"{'Nama':^20} | {'Jumlah Jiwa':^10} | {'Metode':^15} | {'Total':^15} | {'Dibayar':^15} | {'Kembalian':^15} | {'Tanggal':^20}")
    print("-" * 100)
    
    for row in hasil:
        print(f"{row[0]:<20} | {row[1]:^10} | {row[2]:^15} | Rp {float(row[3]):>11,.2f} | Rp {float(row[4]):>11,.2f} | Rp {float(row[5]):>11,.2f} | {row[6]}")
    print("-" * 100)

def tambah_pembayaran():
    db = connect_db()
    cursor = db.cursor()
    try:
        print("\n=== Form Pembayaran Zakat ===")
        nama = input("Nama pembayar: ")
        jumlah_jiwa = int(input("Jumlah jiwa: "))
        jenis_zakat = input("Jenis zakat (beras/uang): ").lower()
        metode = input("Metode pembayaran (Tunai/Transfer): ").lower()
        if metode not in ['tunai', 'transfer']:
            print("Error: Metode pembayaran tidak valid!")
            return
        
        if jenis_zakat == 'beras':
            # Tampilkan daftar harga beras yang tersedia
            daftar_beras = tampilkan_data_beras()
            if not daftar_beras:
                return
                
            # Pilih ID beras
            id_beras = int(input("\nPilih ID beras yang digunakan: "))
            
            # Cari harga beras berdasarkan ID yang dipilih
            harga_beras = None
            for beras in daftar_beras:
                if beras[0] == id_beras:
                    harga_beras = beras[1]
                    break
            
            if not harga_beras:
                print("Error: ID beras tidak valid!")
                return
                
            total_bayar = 3.5 * float(harga_beras) * jumlah_jiwa
            keterangan = f"Beras ID {id_beras}: {3.5 * jumlah_jiwa} Liter"
            
        elif jenis_zakat == 'uang':
            # Pembayaran dengan uang (2.5% dari total pendapatan)
            pendapatan = float(input("Masukkan total pendapatan: Rp "))
            total_bayar = pendapatan * 0.025
            keterangan = f"Uang: 2.5% dari Rp {pendapatan:,.2f}"
            
        else:
            print("Jenis zakat tidak valid!")
            return
        
        print(f"\nTotal yang harus dibayar: Rp {total_bayar:,.2f}")
        print(f"Keterangan: {keterangan}")
        nominal_dibayar = float(input("Masukkan nominal pembayaran: Rp "))
        
        if nominal_dibayar < total_bayar:
            print("Pembayaran kurang!")
            return
            
        kembalian = nominal_dibayar - total_bayar
        tanggal_bayar = datetime.now()

        cursor.execute('''
            INSERT INTO pembayaran 
            (nama, jumlah_jiwa, jenis_zakat, metode_pembayaran, total_bayar, 
             nominal_dibayar, kembalian, keterangan, tanggal_bayar)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (nama, jumlah_jiwa, jenis_zakat, metode, total_bayar, 
              nominal_dibayar, kembalian, keterangan, tanggal_bayar))
        db.commit()
        
        print("\nPembayaran berhasil!")
        print(f"Kembalian: Rp {kembalian:,.2f}")
        
    except ValueError:
        print("Input tidak valid! Pastikan semua input angka berupa numerik.")
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")

def generate_excel_report():
    try:
        # Get payment data
        cursor.execute("""
            SELECT 
                nama, 
                jumlah_jiwa,
                jenis_zakat,
                metode_pembayaran,
                total_bayar,
                nominal_dibayar,
                kembalian,
                keterangan,
                tanggal_bayar
            FROM pembayaran 
            ORDER BY tanggal_bayar DESC
        """)
        payment_data = cursor.fetchall()
        
        if not payment_data:
            print("Tidak ada data untuk di-export")
            return
            
        # Create DataFrame
        df = pd.DataFrame(payment_data, columns=[
            'Nama',
            'Jumlah Jiwa',
            'Jenis Zakat',
            'Metode Pembayaran',
            'Total Bayar',
            'Nominal Dibayar',
            'Kembalian',
            'Keterangan',
            'Tanggal Bayar'
        ])
        
        # Format currency columns
        currency_columns = ['Total Bayar', 'Nominal Dibayar', 'Kembalian']
        for col in currency_columns:
            df[col] = df[col].apply(lambda x: f"Rp {float(x):,.2f}")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'laporan_zakat_{timestamp}.xlsx'
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Write DataFrame to Excel
            df.to_excel(writer, sheet_name='Data Pembayaran', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Data Pembayaran']
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'bg_color': '#D3D3D3'
            })
            
            # Apply formats
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Auto-adjust columns width
            for idx, col in enumerate(df.columns):
                series = df[col]
                max_len = max(
                    series.astype(str).map(len).max(),
                    len(str(series.name))
                ) + 2
                worksheet.set_column(idx, idx, max_len)
        
        print(f"\nLaporan berhasil di-export ke file: {filename}")
        
    except Exception as e:
        print(f"Error saat generate laporan: {str(e)}")



try:
    db = connect_db()
    cursor = db.cursor()
    create_beras_table()
    create_payment_table(db)
except mysql.connector.Error as e:
    print(f"Database connection failed: {e}")
    exit(1)

try:
    while True:
        print("\n=== Menu ===")
        print("1. Tambah Data Beras")
        print("2. Tampilkan Data Beras")
        print("3. Tampilkan Data Pembayaran")
        print("4. Pembayaran Zakat")
        print("5. Export Laporan Excel")
        print("6. Keluar")
        
        pilihan = input("Pilih menu (1-6): ")
        
        if pilihan == '1':
            tambah_data_beras()
        elif pilihan == '2':
            tampilkan_data_beras()
        elif pilihan == '3':
            tampilkan_data_pembayaran()
        elif pilihan == '4':
            tambah_pembayaran()
        elif pilihan == '5':
            generate_excel_report()
        elif pilihan == '6':
            print("Program selesai")
            break
        else:
            print("Pilihan tidak valid!")
finally:
    cursor.close()
    db.close()