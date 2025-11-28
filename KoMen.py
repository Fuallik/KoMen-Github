import psycopg2
import pandas as pd
from datetime import datetime

current_user_id = None

def connectDB():
    try:
        conn = psycopg2.connect(host="localhost", port="5432", user="postgres", password="123", dbname="KoMen")
        cur = conn.cursor()
        #print("mantap")
        return conn, cur
    except Exception:
        print("koneksi gagal")
        return None

def getPetaniIdByAkun(id_akun):
    conn, cur = connectDB()
    cur.execute("SELECT id_petani FROM petani_kopi WHERE akun_id_akun = %s", (id_akun,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def getAdminIdByAkun(id_akun):
    conn, cur = connectDB()
    cur.execute("SELECT id_admin FROM admins WHERE akun_id_akun = %s", (id_akun,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def updateProduct(nama, id_admin):
    try:
        conn, cur = connectDB()
        query_update = "UPDATE admins SET nama = %s WHERE id_admin = %s"
        cur.execute(query_update, (nama, id_admin))
        conn.commit()
        #getAllProduct()
        print("UDAH KEGANTI BOS")
        conn.close()
    except Exception:
        print("ada salahnya bos")
        return None

def login(username, password):
    conn, cur = connectDB()
    query_akun = "SELECT id_akun, role_id_role FROM akun WHERE username = %s AND passwords = %s"
    cur.execute(query_akun, (username, password))
    data = cur.fetchone()
    conn.close()

    if data is None:
        return None, None

    id_akun, role = data

    nama_role = {1: "admin", 
                2: "petani", 
                3: "pembeli"
            }.get(role, "unknown")

    return id_akun, nama_role

def getAllProduct():
    conn, cur = connectDB()
    query_select = "SELECT * FROM admins"

    cur.execute(query_select)
    data = cur.fetchall()
    #for row in data:
    #    print(row)
    data = pd.DataFrame(data, columns=["id admin", "nama", "no telepon"])
    data.index += 1 #memulai index dari 1
    data.drop(columns=[""], inplace=True) #menghapus kolom
    print(data)
    conn.close()

def lihatPenanaman(id_petani):
    conn, cur = connectDB()
    query = """
        SELECT p.id_penanaman, p.jenis_kopi, p.kuantitas, p.tanggal_penanaman, p.deskripsi, d.petani_kopi_id_petani
        FROM data_penanaman p JOIN detail_petani d ON (p.id_penanaman = d.data_penanaman_id_penanaman) 
        WHERE petani_kopi_id_petani = %s
        ORDER BY id_penanaman ASC
    """
    cur.execute(query, (id_petani,))
    data = cur.fetchall()

    if not data:
        print("Belum ada data penanaman.")
        conn.close()
        return

    dataFrame = pd.DataFrame(data, columns=["ID Penanaman", "Jenis Kopi", "Kuantitas", "Tanggal Penanaman", "Deskripsi", "ID Kopi"])
    dataFrame.index += 1
    print("\n=== DATA PENANAMAN ===")
    print(dataFrame)
    conn.close()


####################ADMIN####################
def addPetani():
    conn, cur = connectDB()

    while True:
        print("===TAMBAH AKUN PETANI===")
        username = input("Masukkan Username Petani Baru = ")
        pw = input("Masukkan Password Petani Baru = ")
        nama = input("Masukkan Nama Petani Baru = ")
        alamat = input("Masukkan Alamat Petani Baru = ")
        no_telp = input("Masukkan Nomer Telepon : ")

        query_insert = "INSERT INTO akun(username, passwords, role_id_role) VALUES(%s, %s, 2) RETURNING id_akun"
        cur.execute(query_insert, (username, pw))
        id_akun_baru = cur.fetchone()[0]
        query_insertPet = "INSERT INTO petani_kopi (nama, no_telp, alamat, akun_id_akun) VALUES(%s, %s, %s, %s)"
        cur.execute (query_insertPet, (nama, no_telp, alamat, id_akun_baru))

        conn.commit()
        conn.close()
        return id_akun_baru
        print("Akun Petani Baru Telah Ditambahkan!")

        pilihan = input("Apakah Ingin Melanjutkan Menambah Akun Petani Baru ? [y/n]").lower()
        if pilihan == "y":
            continue
        elif pilihan == "n":
            break
        else:
            print("Pilihan Invalid!")

def delPetani():
    conn, cur = connectDB()
    while True:
        print("===HAPUS AKUN PETANI===")
        lihatAkunPetani()

        username = input("Masukkan Username Petani = ")
        query_akun = "SELECT id_akun FROM akun WHERE username = %s AND role_id_role = 2;"
        cur.execute(query_akun, (username,))
        data = cur.fetchone()

        if not data:
            print("Akun Petani Tidak Ditemukan!")
            return

        id_akun = data[0]

        query_dropPetani = "DELETE FROM petani_kopi WHERE akun_id_akun = %s"
        cur.execute(query_dropPetani, (id_akun,))

        query_dropAkun = "DELETE FROM akun WHERE id_akun = %s"
        cur.execute(query_dropAkun, (id_akun,))

        conn.commit()
        print(f"Akun Petani {username} Telah Dihapus!")

        pilihan = input("Apakah Ingin Melanjutkan Menghapus Akun Petani Baru ? [y/n] : ").lower()
        if pilihan == "y":
            continue
        elif pilihan == "n":
            break
        else:
            print("Pilihan Invalid!")

        conn.close()

def lihatDataHari(): #admin
    conn, cur = connectDB()
    query = """SELECT dh.id_harian, dh.tanggal_penanaman, dh.deskripsi, dp.id_penanaman, dpt.petani_kopi_id_petani
    FROM data_harian dh JOIN data_penanaman dp ON (dh.data_penanaman_id_penanaman = dp.id_penanaman)
    JOIN detail_petani dpt ON (dp.id_penanaman = dpt.data_penanaman_id_penanaman)
    ORDER BY id_harian ASC
    """
    cur.execute(query)
    data = cur.fetchall()

    print("\n===DATA HARIAN===")
    if not data:
        print("Belum Ada Data Perkembangan Dari Petani\n")
        conn.close()
        return
    
    dataFrame = pd.DataFrame(data, columns=["ID Harian", "Tanggal Penanaman", "Deskripsi", "ID Penanaman", "ID Petani"])
    dataFrame.index += 1

    print(dataFrame)

    conn.close()

def stokKopi(): #Admin, Petani, Pembeli
    conn, cur = connectDB()

    query = """
    SELECT id_kopi, jenis_kopi, kualitas, harga, jumlah_stok, deskripsi
    FROM kopi
    ORDER BY id_kopi ASC
    """
    
    cur.execute(query)
    data = cur.fetchall()
    dataFrame = pd.DataFrame(data, columns=["ID Kopi", "Jenis Kopi", "Kualitas", "Harga", "Jumlah Stok", "Deskripsi"])
    dataFrame.index += 1

    if not data:
        print("Stok kopi masih kosong.")
        conn.close()
        return

    dataFrame = pd.DataFrame(data, columns=["ID Kopi", "Jenis Kopi", "Kualitas", "Harga", "Jumlah Stok", "Deskripsi"])
    dataFrame.index += 1

    print("\n===STOK KOPI TERSEDIA===")
    print(dataFrame)

    conn.close()

def verifikasiStok():
    global current_user_id

    id_akun_admin = current_user_id
    id_admin = getAdminIdByAkun(id_akun_admin)

    if id_admin is None:
        print("Data admin tidak ditemukan. Pastikan akun admin sudah terhubung.")
        return

    while True:
        conn, cur = connectDB()

        print("\n===DAFTAR PENGAJUAN STOK (STATUS: pending)===")
        query_pending = """
            SELECT v.id_verifikasi, p.nama, v.tanggal_terverifikasi
            FROM verifikasi v JOIN petani_kopi p ON v.petani_kopi_id_petani = p.id_petani
            WHERE v.status_verifikasi = 'pending'
            ORDER BY v.id_verifikasi ASC"""
        cur.execute(query_pending)
        rows = cur.fetchall()

        if not rows:
            print("Tidak ada pengajuan stok yang sedang pending.")
            conn.close()
            return
        
        for row in rows:
            id_verifikasi, nama_petani, status, tgl = row
            print(f"ID Verifikasi: {id_verifikasi} | Petani: {nama_petani} | Status: {status}")

        try:
            pilih = int(input("\nMasukkan ID verifikasi yang ingin diproses (0 untuk kembali): "))
        except ValueError:
            print("Input tidak valid.")
            conn.close()
            continue

        if pilih == 0:
            conn.close()
            break
        
        query_detail = """
            SELECT v.id_verifikasi, p.nama, d.id_detail_verifikasi, d.kopi_id_kopi, k.jenis_kopi, d.kuantitas, d.jenis_kopi_baru, d.deskripsi_baru, d.harga_baru, d.kualitas_baru
            FROM verifikasi v JOIN petani_kopi p ON v.petani_kopi_id_petani = p.id_petani
            JOIN detail_verifikasi d ON d.verifikasi_id_verifikasi = v.id_verifikasi
            LEFT JOIN kopi k ON k.id_kopi = d.kopi_id_kopi
            WHERE v.id_verifikasi = %s;
        """
        cur.execute(query_detail, (pilih,))
        details = cur.fetchall()

        if not details:
            print("Data verifikasi tidak ditemukan.")
            conn.close()
            continue

        print("\n=== DETAIL PENGAJUAN ===")
        for (id_ver, nama_petani, id_det, id_kopi, jenis_kopi_lama, qty, jenis_baru, desk_baru, harga_baru, kualitas_baru) in details:
            if id_kopi is not None:
                print(f"[KOPI LAMA] ID {id_kopi} - {jenis_kopi_lama} | +{qty} | oleh {nama_petani}")
            else:
                print("[KOPI BARU]")
                print(f"  Jenis     : {jenis_baru}")
                print(f"  Deskripsi : {desk_baru}")
                print(f"  Harga     : {harga_baru}")
                print(f"  Stok awal : {qty}")
                print(f"  Kualitas  : {kualitas_baru}")
                print(f"  Diajukan oleh: {nama_petani}")

        keputusan = input("\nSetujui pengajuan ini? [y/n] : ").lower()

        if keputusan == "y":
            for (id_ver, nama_petani, id_det, id_kopi, jenis_kopi_lama, qty, 
            jenis_baru, desk_baru, harga_baru, kualitas_baru) in details:

                if id_kopi is not None:

                    cur.execute(
                        "UPDATE kopi SET jumlah_stok = jumlah_stok + %s WHERE id_kopi = %s",
                        (qty, id_kopi)
                    )
                else:

                    cur.execute("""
                        INSERT INTO kopi (jenis_kopi, deskripsi, harga, jumlah_stok, kualitas)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id_kopi""", (jenis_baru, desk_baru, harga_baru, qty, kualitas_baru))
                    new_id_kopi = cur.fetchone()[0]

                    cur.execute("""
                        UPDATE detail_verifikasi
                        SET kopi_id_kopi = %s
                        WHERE id_detail_verifikasi = %s
                    """, (new_id_kopi, id_det))

            cur.execute("""
                UPDATE verifikasi
                SET status_verifikasi = 'disetujui', admins_id_admin = %s, tanggal_terverifikasi = CURRENT_DATE
                WHERE id_verifikasi = %s""", (id_admin, pilih))

            conn.commit()
            print("Pengajuan telah DISETUJUI. Stok kopi sudah diperbarui / kopi baru sudah dibuat.")

        elif keputusan == "n":
            cur.execute("""
                UPDATE verifikasi
                SET status_verifikasi = 'ditolak', admins_id_admin = %s, tanggal_terverifikasi = CURRENT_DATE
                WHERE id_verifikasi = %s""", (id_admin, pilih))

            conn.commit()
            print("Pengajuan telah DITOLAK. Stok kopi tidak berubah.")

        else:
            print("Pilihan tidak valid. Tidak ada perubahan.")

        conn.close()

        lanjut = input("\nProses pengajuan lain? [y/n]: ").lower()
        if lanjut != "y":
            break

def feedback(id_admin): #Admin
    conn, cur = connectDB()
    global admins_id_admin 

    print("=== FEEDBACK ADMIN ===")
    lihatDataHari()
    
    id_data_harian = input("Masukkan ID Data Harian = ")
    catatan_feedback = input("Masukkan Feedback = ")

    query = """INSERT INTO feedback (admins_id_admin, data_harian_id_harian, tanggal_feedback, catatan_feedback)
    VALUES (%s, %s, CURRENT_DATE, %s)
    RETURNING id_feedback"""

    cur.execute(query, (id_admin, id_data_harian, catatan_feedback))

    id_feedback_baru = cur.fetchone()[0]
    conn.commit()
    conn.close()

    print("Feedback berhasil dikirim!")
    print(f"ID Feedback : {id_feedback_baru}")

####################PETANI####################
def dataPenanaman(id_petani):
    conn, cur = connectDB()

    print("===INPUT DATA PENANAMAN===")
    print("1. Pakai jenis kopi yang SUDAH ADA di tabel kopi")
    print("2. Catat JENIS KOPI BARU (belum ada di tabel kopi)")
    pilihan = int(input("Pilih [1/2] : "))

    jenis_kopi = input("Masukkan Jenis Kopi: ").capitalize()
    tanggal_penanaman = input("Masukkan Tanggal Penanaman (YYYY-MM-DD): ")
    kuantitas = int(input("Masukkan Kuantitas: "))   
    deskripsi = input("Masukkan Deskripsi: ")

    query_insert = """INSERT INTO data_penanaman (jenis_kopi,tanggal_penanaman, kuantitas, deskripsi)
    VALUES (%s, %s, %s, %s)RETURNING id_penanaman"""
    
    cur.execute(query_insert, (jenis_kopi,tanggal_penanaman, kuantitas, deskripsi))
    id_penanaman = cur.fetchone()[0]

    if pilihan == 1:
        stokKopi()
        try:
            id_kopi = int(input("Masukkan ID Kopi (sesuai tabel kopi): "))
        except ValueError:
            print("ID kopi harus berupa angka!")
            conn.rollback()
            conn.close()
            return
        
        cur.execute("SELECT 1 FROM kopi WHERE id_kopi = %s", (id_kopi,))
        if not cur.fetchone():
            print("ID kopi tidak ditemukan di tabel kopi.")
            conn.rollback()
            conn.close()
            return

        query_insertDet = """INSERT INTO detail_petani (petani_kopi_id_petani, data_penanaman_id_penanaman, kopi_id_kopi) 
        VALUES (%s, %s, %s)"""
        cur.execute(query_insertDet, (id_petani, id_penanaman, id_kopi))

    elif pilihan == 2:
        query_insertDet = """INSERT INTO detail_petani (petani_kopi_id_petani, data_penanaman_id_penanaman, kopi_id_kopi)
        VALUES (%s, %s, NULL)"""
        cur.execute(query_insertDet, (id_petani, id_penanaman))

    else:
        print("Pilihan Invalid!")
        conn.rollback()
        conn.close()
        return

    conn.commit()
    conn.close()

    print("Data Penanaman Telah Ditambahkan!")

def dataHari(id_petani):
    conn, cur = connectDB()

    print("===INPUT DATA PERKEMBANGAN TANAMAN===")
    lihatPenanaman(id_petani)

    id_penanaman = input("Masukkan ID Penanaman yang ingin ditambahkan perkembangan: ")

    query_check = """SELECT p.id_penanaman, kopi_id_kopi FROM data_penanaman p
    JOIN detail_petani d ON (p.id_penanaman = d.data_penanaman_id_penanaman)
    WHERE p.id_penanaman = %s AND d.petani_kopi_id_petani = %s"""
    
    cur.execute(query_check, (id_penanaman, id_petani))
    if not cur.fetchone():
        print("ID penanaman tidak ditemukan atau bukan milik Anda!")
        conn.close()
        return
    
    print("=== DATA PENANAMAN ANDA ===")

    deskripsi = input("Masukkan deskripsi perkembangan: ")
    tanggal = datetime.now()
    
    query_insert = """INSERT INTO data_harian (data_penanaman_id_penanaman, tanggal_penanaman, deskripsi)
    VALUES (%s, %s, %s)"""
    cur.execute(query_insert, (id_penanaman, tanggal, deskripsi))

    conn.commit()
    conn.close()
    print("\nPerkembangan berhasil ditambahkan!\n")

def ajuStok():
    conn, cur = connectDB()
    global current_user_id

    id_akun_petani = current_user_id
    id_petani = getPetaniIdByAkun(id_akun_petani)
    
    if id_petani is None:
        print("Data petani tidak ditemukan. Pastikan akun petani sudah terhubung.")
        return

    while True:
        print("\n=== PENGAJUAN STOK KOPI ===")
        print("1. Ajukan stok kopi yang SUDAH ADA")
        print("2. Ajukan kopi JENIS BARU")
        print("3. Kembali ke menu sebelumnya")
        pilihan = int(input("Pilih [1/2/3]: "))

        
        if pilihan == 1:
            conn, cur = connectDB()
            print("===PENGAJUAN STOK KOPI===")
            stokKopi()

            id_kopi = input("Masukkan ID Kopi yang ingin diajukan stoknya : ")

            try:
                kuantitas = int(input("Masukkan jumlah stok yang diajukan : "))
            except ValueError:
                print("Kuantitas harus berupa angka!")
                conn.close()
                continue

            cur.execute("SELECT jenis_kopi FROM kopi WHERE id_kopi = %s", (id_kopi,))
            row = cur.fetchone()
            if not row:
                print("ID kopi tidak ditemukan!")
                conn.close()
                lanjut = input("Ajukan lagi? [y/n]: ").lower()
                if lanjut != "y":
                    break
                else:
                    continue

            query_verifikasi = """
            INSERT INTO verifikasi (admins_id_admin, petani_kopi_id_petani, status_verifikasi, tanggal_terverifikasi)
            VALUES (NULL, %s, 'pending', NULL)
            RETURNING id_verifikasi"""
            cur.execute(query_verifikasi, (id_petani,))
            id_verifikasi = cur.fetchone()[0]
            query_detail = """INSERT INTO detail_verifikasi (kuantitas, verifikasi_id_verifikasi, kopi_id_kopi)
            VALUES (%s, %s, %s)"""
            cur.execute(query_detail, (kuantitas, id_verifikasi, id_kopi))

            conn.commit()
            conn.close()

            print(f"Pengajuan stok berhasil dikirim dengan ID verifikasi {id_verifikasi}.")
            print("Status: pending, menunggu persetujuan admin.\n")

        elif pilihan == 2:
            conn, cur = connectDB()

            print("\n=== PENGAJUAN KOPI JENIS BARU ===")
            jenis_kopi = input("Masukkan Jenis Kopi Baru   : ").capitalize()
            deskripsi = input("Masukkan Deskripsi Kopi    : ")
            try:
                harga = int(input("Masukkan Harga Kopi        : "))
                kuantitas = int(input("Masukkan Jumlah Stok Awal  : "))
            except ValueError:
                print("Harga dan kuantitas harus berupa angka!")
                conn.close()
                continue
            kualitas = input("Masukkan Kualitas Kopi     : ")
            query_verifikasi = """
                INSERT INTO verifikasi (admins_id_admin, petani_kopi_id_petani, status_verifikasi, tanggal_terverifikasi)
                VALUES (NULL, %s, 'pending', NULL)
                RETURNING id_verifikasi"""
            cur.execute(query_verifikasi, (id_petani,))
            id_verifikasi = cur.fetchone()[0]

            query_detail = """
                INSERT INTO detail_verifikasi (kuantitas, verifikasi_id_verifikasi, kopi_id_kopi, jenis_kopi_baru, deskripsi_baru, harga_baru, kualitas_baru)
                VALUES (%s, %s, NULL, %s, %s, %s, %s)"""
            cur.execute(
                query_detail,
                (kuantitas, id_verifikasi, jenis_kopi, deskripsi, harga, kualitas)
            )

            conn.commit()
            conn.close()

            print(f"Pengajuan KOPI BARU berhasil dikirim dengan ID verifikasi {id_verifikasi}.")
            print("Status: pending, menunggu persetujuan admin.\n")
        
        elif pilihan == "3":
            break
        else:
            print("Pilihan tidak valid!")

        lanjut = input("Ajukan lagi? [y/n]: ").lower()
        if lanjut != "y":
            break

def mail(id_petani):
    conn, cur = connectDB()
    query_select = """SELECT f.id_feedback, f.catatan_feedback, d.id_harian, d.deskripsi, d.tanggal_penanaman, dp.petani_kopi_id_petani
    FROM feedback f JOIN data_harian d ON (d.id_harian = f.data_harian_id_harian)
    JOIN data_penanaman dm ON (dm.id_penanaman = d.data_penanaman_id_penanaman)
    JOIN detail_petani dp ON (dm.id_penanaman = dp.data_penanaman_id_penanaman)
    WHERE dp.petani_kopi_id_petani = %s"""

    cur.execute(query_select, (id_petani,))
    hasil = cur.fetchall()

    print("\n=== FEEDBACK UNTUK DATA HARIAN ANDA ===")

    if not hasil:
        print("Belum ada feedback dari admin.")
        return

    df = pd.DataFrame(hasil, columns=["ID Feedback", "Catatan Feedback", "ID Harian", "Deskripsi", "Tanggal Penanaman", "ID Petani"])
    df.index += 1
    print("===MAIL FEEDBACK ANDA===")
    print(df)


####################PEMBELI####################
def orderKopi():
    global current_user_id
    conn, cur = connectDB()
    stokKopi()
    
    id_kopi = input("Masukkan ID Kopi : ")
    jumlah = int(input("Masukkan Jumlah : "))
    cur.execute("SELECT harga, jumlah_stok, jenis_kopi FROM kopi WHERE id_kopi = %s", (id_kopi,))
    row = cur.fetchone()

    if not row:
        print("ID kopi tidak ditemukan!")
        conn.close()
        return

    harga, jumlah_stok, jenis_kopi = row
    if jumlah > jumlah_stok:
        print(f"Stok tidak cukup! Tersedia: {jumlah_stok}")
        conn.close()
        return

    total = harga * jumlah

    print(f"Total bayar untuk {jumlah} x {jenis_kopi} = {total}")
    input("Tekan Enter untuk membayar...")

    status = "Lunas"
    tanggal = datetime.now()

    query_insertOrders = ("""INSERT INTO orders (tanggal_order, transaksi_id_transaksi, pembeli_id_pembeli) 
    VALUES (%s, NULL, %s) RETURNING id_order""")
    cur.execute(query_insertOrders, (tanggal, current_user_id))
    id_order = cur.fetchone()[0]

    query_updateKopi = ("UPDATE kopi SET jumlah_stok = jumlah_stok - %s WHERE id_kopi = %s")
    cur.execute(query_updateKopi, (jumlah, id_kopi))

    query_insertDetOrd = ("""INSERT INTO order_detail (harga, kuantitas, orders_id_order, kopi_id_kopi)
    VALUES (%s, %s, %s, %s)""")
    cur.execute(query_insertDetOrd, (harga, jumlah, id_order, id_kopi))

    query_insertTransaksi = ("""INSERT INTO transaksi (tanggal_transaksi, status_pembayaran, orders_id_order)
    VALUES (%s, %s, %s) RETURNING id_transaksi""")   
    cur.execute(query_insertTransaksi, (tanggal, status, id_order))
    id_transaksi = cur.fetchone()[0]

    query_updateOrders = ("UPDATE orders SET transaksi_id_transaksi = %s WHERE id_order = %s")
    cur.execute(query_updateOrders, (id_transaksi, id_order))

    conn.commit()
    conn.close()
    print(f"Pembelian berhasil! Status pembayaran: {status} | Tanggal: {tanggal}\n")

def history():
    global current_user_id

    if current_user_id is None:
        print("Anda belum login!")
        return

    try:
        conn, cur = connectDB()

        query_select = ("""SELECT o.id_order, k.id_kopi, od.kuantitas, od.harga, o.tanggal_order, t.status_pembayaran, (od.harga * od.kuantitas) as total
        FROM order_detail od join orders o on (o.id_order = od.orders_id_order)
        join kopi k on (k.id_kopi = od.kopi_id_kopi)
        join transaksi t on (t.id_transaksi = o.transaksi_id_transaksi)
        WHERE o.pembeli_id_pembeli = %s
        ORDER BY o.tanggal_order""")
        cur.execute(query_select, (current_user_id,))
        data = cur.fetchall()
        conn.close()

        if not data:
            print("Riwayat pembelian masih kosong.")
            return

        print("=== RIWAYAT PEMBELIAN ===")
        for row in data:
            print(f"ID Order     : {row[0]}")
            print(f"ID Kopi      : {row[1]}")
            print(f"Jumlah       : {row[2]}")
            print(f"Harga        : Rp {row[3]}")
            print(f"Tanggal      : {row[4]}")
            print(f"Status Bayar : {row[5]}")
            print(f"Total        : Rp {row[6]}")
            print("-----------------------------")

    except Exception as e:
        print("Gagal mengambil riwayat:", e)

def addKopi(tanggal_penanaman, deskripsi):
    conn, cur = connectDB()
    query_insert = "INSERT INTO data_penanaman(tanggal_penanaman, deskripsi) VALUES(%s, %s)"

    cur.execute(query_insert, (tanggal_penanaman, deskripsi))
    conn.commit()
    print('Data Telah ditambahkan')
    conn.close()

def addstokKopi(): #Admin
    while True:
        conn, cur = connectDB()
    
        stokKopi()
        id_kopi = int(input("Masukkan ID Kopi : "))
        jumlah_stok = int(input("Masukkan Jumlah Stok : "))
    
        query_select = "SELECT jumlah_stok FROM kopi WHERE id_kopi = %s"
        cur.execute(query_select, (id_kopi,))
        data = cur.fetchone()
    
        if data is None:
            print("Data Tidak Ditemukan!")
            pilihan = input("Apalah Anda Ingin Menambah Data Baru? Pilih y/n : ")

            if pilihan == "y":
                print("===TAMBAH STOK BARU===")

                jenis_kopi = input("Masukkan Jenis Kopi Baru : ")
                nama_kopi = input("Masukkan Nama Kopi : ")
                deskripsi = input("Masukkan Deskripsi Kopi : ")
                harga = int(input("Masukkan Harga Kopi : "))
                jumlah_stok = int(input("Masukkan Jumlah Stok Kopi : "))
                kualitas = input("Masukkan Kualitas Kopi : ")

                query_insert = "INSERT INTO kopi(jenis_kopi, nama_kopi, deskripsi, harga, jumlah_stok, kualitas) VALUES (%s, %s, %s, %s, %s, %s)"
                cur.execute(query_insert, (jenis_kopi, nama_kopi, deskripsi, harga, jumlah_stok, kualitas))
                conn.commit()
                print("Data Kopi Baru Telah Ditambah!")
                conn.close()

                pilihan = input("Apakah anda ingin melanjutkan menambah kopi? [y/n]").lower()
                if pilihan == "y":
                    continue
                elif pilihan == "n":
                    break
                else:
                    print("Pilihan Invalid!")


            elif pilihan == "n":
                print("Program Penambahan Kopi Telah Dihentikan!")
                break

            else:
                print("Pilihan Invalid!")

        else:
            print("===UPDATE STOCK===")
            
            id_kopi = input("Masukkan ID Kopi : ")
            jumlah_stok = input("Masukkan Jumlah Stok : ")

            query_update = "UPDATE kopi SET jumlah_stok = jumlah_stok + %s WHERE id_kopi = %s"
            cur.execute(query_update, (jumlah_stok, id_kopi))
    
            conn.commit()
            print("Stok Telah Diubah!")
            conn.close()

            print("Apakah anda ingin melanjutkan menambah stok kopi? [y/n]")
            pilihan = input().lower()
            if pilihan == "y":
                continue
            elif pilihan == "n":
                break
            else:
                print("Pilihan Invalid!")

def lihatAkunPetani():
    conn, cur = connectDB()

    query_select = """SELECT p.id_petani, p.nama, p.akun_id_akun, a.username FROM petani_kopi p join akun a on (p.akun_id_akun = a.id_akun)
    ORDER BY id_petani ASC"""
    cur.execute(query_select)
    rows = cur.fetchall()

    if not rows:
        print("===DATA PETANI KOSONG===")
        return
    df = pd.DataFrame(rows, columns=["ID Petani", "Nama Petani", "ID Akun", "Username"])
    df.index += 1
    print("===DATA PETANI===")
    print(df)

    conn.close()

def daRiPetani(): #Admin
    conn, cur = connectDB()

    query = """SELECT id_harian, data_penanaman_id_penanaman, tanggal_penamanan, kualitas, deskripsi,
    FROM dat_harian
    ORDER BY tanggal_penanaman ASC"""
    
    cur.execute(query)
    data = cur.fetchall()
    dataFrame = pd.DataFrame(data, columns=["id_harian", "data_penanaman_id_penanaman", "tanggal_penamanan", "kualitas", "deskripsi"])
    dataFrame.index += 1

    if not data:
        print("Data Harian Petani masih kosong.")
        conn.close()
        return

    df = pd.DataFrame(data, columns=["ID Data Harian", "ID Penanaman", "Tanggal Penanaman", "Kualitas", "Deskripsi"])

    df.index += 1  # mulai index dari 1

    print("\n=== DATA HARIAN PETANI ===")
    print(df)

    conn.close()

#####################MAIN####################

def mainRegister():
    conn, cur = connectDB()

    print("===REGISTER===")
    username = input("Masukkan username = ")
    password = input("Masukkan password = ")
    nama = input("Masukkan nama = ")
    no_telp = input("Masukkan no telpon aktif = ")
    alamat = input("Masukkan alamat = ")

    query_insertAkun = "INSERT INTO akun (username, passwords, role_id_role) VALUES (%s, %s, 3) RETURNING id_akun"
    cur.execute(query_insertAkun, (username, password))
    id_akun_baru = cur.fetchone()[0]

    query_insertPembeli = "INSERT INTO pembeli (nama, no_telp, alamat, akun_id_akun) VALUES (%s, %s, %s, %s)"
    cur.execute(query_insertPembeli, (nama, no_telp, alamat, id_akun_baru))

    conn.commit()
    conn.close()

    print("Berhasil Membuat Akun!")
    print(f"ID Akun : {id_akun_baru}")

def mainLogin():
    global current_user_id
    global admins_id_admin
    conn, cur = connectDB()

    print("===LOGIN===")
    username = input("Masukkan username = ")
    password = input("Masukkan password = ")
    id_akun, role = login(username, password)

    query_select = """SELECT a.id_akun, r.nama_role, p.id_pembeli
    FROM akun a JOIN roles r ON a.role_id_role = r.id_role
    LEFT JOIN pembeli p ON p.akun_id_akun = a.id_akun
    WHERE a.username = %s AND a.passwords = %s"""

    cur.execute(query_select, (username, password))
    row = cur.fetchone()

    if not row:
        print("Login gagal!")
        return False

    id_akun, role, id_pembeli = row

    if role == "pembeli":
        current_user_id = id_pembeli
    else:
        current_user_id = id_akun


    print("Login berhasil sebagai:", role)

    if role == "admin":
        print("Anda login sebagai admin")
        mainAdmin()
    elif role == "petani":
        print("Anda login sebagai petani")
        mainPetani()
    elif role == "pembeli":
        print("Anda login sebagai pembeli")
        mainPembeli()
    else:
        print("ERROR: Role tidak diketahui")

    conn.close()
    return True

def mainAdmin():
    global current_user_id

    id_akun_admin = current_user_id
    id_admin = getAdminIdByAkun(id_akun_admin)

    if id_admin is None:
        print("Data admin tidak ditemukan. Pastikan akun admin sudah terhubung.")
        return
        
    while True:
        print("===MAIN ADMIN===")
        print("1. Tambah Akun Petani") #sudah benar
        print("2. Hapus Akun Petani") #sudah benar
        print("3. Menampilkan Data Harian Petani") #sudah benar
        print("4. Menampilkan Stok Kopi") #sudah benar
        print("5. Verifikasi Pengajuan Stok Kopi") #sudah benar
        print("6. Feedback")
        print("7. LogOut")
     
        pilihan = int(input("Masukkan pilihan : "))
        if pilihan == 1:
            addPetani()
        elif pilihan == 2:
            delPetani()
        elif pilihan == 3:
            lihatDataHari()
        elif pilihan == 4:
            stokKopi()
        elif pilihan == 5:
            verifikasiStok()
        elif pilihan == 6:
            feedback(id_admin)
        elif pilihan == 7:
            print("Anda Telah LogOut, Terima Kasih!")
            break
        else:
            print("Pilihan Invalid!")

def mainPetani():
    global current_user_id

    id_akun_petani = current_user_id
    id_petani = getPetaniIdByAkun(id_akun_petani)
    if id_petani is None:
        print("Data petani tidak ditemukan.")
        return

    while True:
        print("===MAIN PETANI===")
        print("1. Input Data Awal Penanaman") #sudah benar
        print("2. Input Data Perkembangan tanaman") #sudah benar
        print("3. Mail Feedback")
        print("4. Pengajuan Stok") #sudah benar
        print("5. LogOut")

        pilihan = int(input("Masukkan pilihan : "))
        if pilihan == 1:
            dataPenanaman(id_petani)
        elif pilihan == 2:
            dataHari(id_petani)
        elif pilihan == 3:
            mail(id_petani)
        elif pilihan == 4:
            ajuStok()
        elif pilihan == 5:
            print("Anda Telah LogOut, Terima Kasih!")
            break
        else:
            print("Pilihan Invalid!")

def mainPembeli():
    while True:
        print("===MAIN PEMBELI===")
        print("1. Tampilkan Stok Kopi") #sudah benar
        print("2. Order Kopi") #sudah benar
        print("3. History Pembelian") #sudah benar
        print("4. LogOut")
        
        pilihan = int(input("Masukkan Pilihan : "))
        if pilihan == 1:
            stokKopi()
        elif pilihan == 2:
            orderKopi()
        elif pilihan == 3:
            history()
        elif pilihan == 4:
            print("Anda Telah LogOut, Terima Kasih!")
            break
        else:
            print("Pilihan Invalid!")

def KoMen():
    while True:
        print("===MENU===")
        print("1. Register")
        print("2. Login")
        print("3. Keluar")
        
        pilihan = int(input("Masukkan Pilihan : "))
        if pilihan == 1:
            mainRegister()
        elif pilihan == 2:
            mainLogin()
        elif pilihan == 3:
            print("Program Telah Dihentikan, Terima Kasih!")
            break
        else:
            print("Pilihan Invalid")

KoMen()








#addKopi("27-10-2025", "kopi jayapura") ini buat nambah
#getAdminsById(1)
#updateProduct('Semi God Bintang', 2)
