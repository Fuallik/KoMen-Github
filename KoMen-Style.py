import psycopg2
import pandas as pd
from datetime import datetime
import os
import msvcrt  # untuk baca tombol panah di Windows
from tabulate import tabulate
import pyfiglet
from colorama import Fore, Style, init
import questionary

current_user_id = None

########### STYLES ##############

COFFEE    = "\033[38;5;94m"   # warna coklat kopi (menu & judul)
RESET     = "\033[0m"
HIGHLIGHT = "\033[7m"         # highlight baris aktif

# warna khusus untuk TABEL
TABLE_BORDER = "\033[38;5;178m"  # kuning emas untuk garis tabel
TABLE_TEXT   = "\033[97m"        # putih terang untuk teks tabel

def menu_kopi(title: str, options: list[str]) -> int:
    """
    Menampilkan menu dengan tema kopi dan border rounded.
    Kontrol:
      - Arrow UP   : pindah ke atas
      - Arrow DOWN : pindah ke bawah
      - Enter      : pilih
    """
    selected = 0
    first_render = True

    # 1 (blank) + 1 (header) + 1 (title) + 1 (separator) + n (options) + 1 (footer) + 1 (hint)
    total_lines = 1 + 1 + 1 + 1 + len(options) + 1 + 1

    # sembunyikan kursor
    print("\033[?25l", end="")

    try:
        while True:
            if not first_render:
                # naik lagi ke atas area menu
                print("\r\033[{}A".format(total_lines), end="")
            else:
                first_render = False

            # TIDAK pake angka lagi, cuma teks option
            raw_lines = [opt for opt in options]
            lines = []
            for i, line in enumerate(raw_lines):
                prefix = "▶" if i == selected else " "   # arrow di opsi terpilih
                lines.append(f"{prefix} {line}")

            max_len = max(len(line) for line in lines)
            width   = max(max_len, len(title)) + 4

            # ===== gambar menu =====
            print()  # baris kosong

            # header
            print(COFFEE + "╭" + "─" * width + "╮" + RESET)
            print(
                COFFEE + "│ " + RESET +
                COFFEE + title.center(width-2) + RESET +
                COFFEE + " │" + RESET
            )
            print(COFFEE + "├" + "─" * width + "┤" + RESET)

            # isi menu
            for i, line in enumerate(lines):
                if i == selected:
                    # baris terpilih: background abu, teks tetap warna kopi
                    inner = HIGHLIGHT + COFFEE + line.ljust(width-2) + RESET
                else:
                    # baris biasa: teks warna kopi
                    inner = COFFEE + line.ljust(width-2) + RESET

                print(
                    COFFEE + "│ " + RESET +
                    inner +
                    COFFEE + " │" + RESET
                )

            # footer
            print(COFFEE + "╰" + "─" * width + "╯" + RESET)
            print("↑/↓ : pilih menu   Enter : OK", flush=True)

            # ===== baca tombol =====
            import msvcrt
            key = msvcrt.getch()

            if key == b'\xe0':  # arrow keys
                key2 = msvcrt.getch()
                if key2 == b'H':      # Up
                    selected = (selected - 1) % len(options)
                elif key2 == b'P':    # Down
                    selected = (selected + 1) % len(options)

            elif key in (b'\r', b'\n'):  # Enter
                print()
                return selected + 1

            # tombol lain diabaikan

    finally:
        # tampilkan lagi kursor
        print("\033[?25h", end="")

# inisialisasi colorama
init(autoreset=True)

TITLE = Fore.LIGHTYELLOW_EX + Style.BRIGHT
INFO  = Fore.LIGHTWHITE_EX
ERROR = Fore.LIGHTRED_EX

def banner_komen():
    """Banner besar di awal program."""
    os.system("cls")
    text = pyfiglet.figlet_format("KoMen", font="slant")
    print(COFFEE + text + RESET)

def section_title(text: str):
    """Judul seksi/menu kecil (Tambah Akun Admin, Order Kopi, dsb)."""
    bar = "─" * (len(text) + 2)
    print()
    print(COFFEE + f"╭{bar}╮")
    print(f"│ {text} │")
    print(f"╰{bar}╯" + RESET)

def info(text: str):
    print(INFO + f"[i] {text}" + RESET)

def warn(text: str):
    print(ERROR + f"[!] {text}" + RESET)

def print_df_kopi(df: pd.DataFrame, title: str | None = None):
    """
    Cetak DataFrame dengan tema kopi:
      - Border tabel warna kuning
      - Teks isi tabel warna putih
      - Bentuk tabel rounded_outline (tabulate)
    """
    if df is None or df.empty:
        print("Tabel kosong.")
        return

    # judul opsional di atas tabel
    if title:
        bar = "─" * (len(title) + 2)
        print()
        print(COFFEE + f"╭{bar}╮")
        print(f"│ {title} │")
        print(f"╰{bar}╯" + RESET)

    df_show = df.copy()
    df_show.index = range(1, len(df_show) + 1)

    raw = tabulate(
        df_show,
        headers="keys",
        tablefmt="rounded_outline",
        showindex=True
    )

    border_chars = "╭╮╰╯│├┤┬┴┼─═"

    for line in raw.splitlines():
        buf = []
        for ch in line:
            if ch in border_chars:
                buf.append(TABLE_BORDER + ch + RESET)
            else:
                buf.append(TABLE_TEXT + ch + RESET)
        print("".join(buf))

########### DATABASE TOOLS ##############

def connectDB():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="123",
            dbname="KoMen"
        )
        cur = conn.cursor()
        return conn, cur
    except Exception:
        print("Koneksi gagal")
        return None

def getPetaniIdByAkun(id_akun):
    try:
        conn, cur = connectDB()
        cur.execute("SELECT id_petani FROM petani_kopi WHERE id_akun = %s", (id_akun,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        print("Terjadi kesalahan di fungsi getPetaniIdByAkun")
        return None

def getAdminIdByAkun(id_akun):
    try:
        conn, cur = connectDB()
        cur.execute("SELECT id_admin FROM admins WHERE id_akun = %s", (id_akun,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        print("Terjadi kesalahan di fungsi getAdminIdByAkun")
        return None

def updateProduct(nama, id_admin):
    try:
        conn, cur = connectDB()
        query_update = "UPDATE admins SET nama = %s WHERE id_admin = %s"
        cur.execute(query_update, (nama, id_admin))
        conn.commit()
        print("UDAH KEGANTI BOS")
        conn.close()
    except Exception:
        print("Terjadi kesalahan di fungsi updateProduct")
        return None

def login(username, password):
    try:
        conn, cur = connectDB()
        query_akun = "SELECT id_akun, id_role FROM akun WHERE username = %s AND passwords = %s"
        cur.execute(query_akun, (username, password))
        data = cur.fetchone()
        conn.close()

        if data is None:
            return None, None

        id_akun, role = data

        nama_role = {
            1: "admin",
            2: "petani",
            3: "pembeli"
        }.get(role, "unknown")

        return id_akun, nama_role
    except Exception:
        print("Terjadi kesalahan di fungsi login")
        return None, None

def getAllProduct():
    try:
        conn, cur = connectDB()
        query_select = "SELECT * FROM admins"

        cur.execute(query_select)
        data = cur.fetchall()
        data = pd.DataFrame(data, columns=["id admin", "nama", "no telepon"])
        print_df_kopi(data, "DATA ADMIN (RAW)")
        conn.close()
    except Exception:
        print("Terjadi kesalahan di fungsi getAllProduct")
        return None

def lihatPenanaman(id_petani):
    conn, cur = connectDB()
    query = """
        SELECT p.id_penanaman,
               p.jenis_kopi,
               p.kuantitas,
               p.tanggal_penanaman,
               p.deskripsi,
               d.id_petani
        FROM data_penanaman p
        JOIN detail_petani d ON (p.id_penanaman = d.id_penanaman) 
        WHERE id_petani = %s
        ORDER BY id_penanaman ASC
    """
    cur.execute(query, (id_petani,))
    data = cur.fetchall()

    if not data:
        print("Belum ada data penanaman.")
        conn.close()
        return

    dataFrame = pd.DataFrame(
        data,
        columns=[
            "ID Penanaman",
            "Jenis Kopi",
            "Kuantitas",
            "Tanggal Penanaman",
            "Deskripsi",
            "ID Petani"
        ]
    )

    print_df_kopi(dataFrame, "DATA PENANAMAN")
    conn.close()

#################### ADMIN ####################

def addAdmin():
    conn, cur = connectDB()

    while True:
        section_title("TAMBAH AKUN ADMIN")

        username = input("Username Admin Baru  : ")
        pw       = input("Password Admin Baru  : ")
        nama     = input("Nama Admin Baru      : ").title()
        no_telp  = input("Nomor Telepon        : ")

        query_insert = """
            INSERT INTO akun (username, passwords, id_role)
            VALUES (%s, %s, 1) RETURNING id_akun
        """
        cur.execute(query_insert, (username, pw))
        id_akun_baru = cur.fetchone()[0]
            
        query_insertAd = """
            INSERT INTO admins (nama, no_telp, id_akun)
            VALUES (%s, %s, %s)
        """
        cur.execute(query_insertAd, (nama, no_telp, id_akun_baru))

        conn.commit()

        info("Akun Admin Baru Telah Ditambahkan!")
        print(f" - Nama     : {nama}")
        print(f" - Username : {username}")
        print(f" - No. Telp : {no_telp}")

        pilihan = input("\nTambah akun admin lain? [y/n]: ").lower()
        if pilihan == "y":
            continue
        elif pilihan == "n":
            break
        else:
            warn("Pilihan Invalid!")
        
        conn.close()
        return id_akun_baru

def delAdmin():
    conn, cur = connectDB()
    while True:
        section_title("HAPUS AKUN ADMIN")
        lihatAkunAdmin()

        username = input("Masukkan Username Admin : ")
        query_akun = "SELECT id_akun FROM akun WHERE username = %s AND id_role = 1"
        cur.execute(query_akun, (username,))
        data = cur.fetchone()

        if not data:
            warn("Akun Admin Tidak Ditemukan!")
            return

        id_akun = data[0]

        query_dropAdmin = "DELETE FROM admins WHERE id_akun = %s"
        cur.execute(query_dropAdmin, (id_akun,))

        query_dropAkun = "DELETE FROM akun WHERE id_akun = %s"
        cur.execute(query_dropAkun, (id_akun,))

        conn.commit()
        info(f"Akun Admin {username} Telah Dihapus!")

        pilihan = input("Hapus akun admin lain? [y/n]: ").lower()
        if pilihan == "y":
            continue
        elif pilihan == "n":
            break
        else:
            warn("Pilihan Invalid!")

    conn.close()

def addPetani():
    conn, cur = connectDB()

    while True:
        section_title("TAMBAH AKUN PETANI")

        username = input("Masukkan Username Petani Baru : ")
        pw       = input("Masukkan Password Petani Baru : ")
        nama     = input("Masukkan Nama Petani Baru     : ").title()
        alamat   = input("Masukkan Alamat Petani Baru   : ").title()
        lurah    = input("Masukkan Kelurahan Petani     : ").title()
        camat    = input("Masukkan Kecamatan Petani     : ").title()
        no_telp  = input("Masukkan Nomor Telepon        : ")

        query_insert = """
            INSERT INTO akun(username, passwords, id_role)
            VALUES(%s, %s, 2) RETURNING id_akun
        """
        cur.execute(query_insert, (username, pw))
        id_akun_baru = cur.fetchone()[0]
        
        query_checkCamat = """
            SELECT id_kecamatan FROM kecamatan
            WHERE LOWER(nama_kecamatan) = LOWER(%s)
        """
        cur.execute(query_checkCamat, (camat,))
        hasil = cur.fetchone()

        if hasil:
            id_kecamatan = hasil[0]
        else:
            query_insertCamat = """
                INSERT INTO kecamatan (nama_kecamatan)
                VALUES (%s) RETURNING id_kecamatan
            """
            cur.execute(query_insertCamat, (camat,))
            id_kecamatan = cur.fetchone()[0]

        query_checkLurah = """
            SELECT id_kelurahan FROM kelurahan
            WHERE LOWER(nama_kelurahan) = LOWER(%s)
              AND id_kecamatan = %s
        """
        cur.execute(query_checkLurah, (lurah, id_kecamatan))
        hasilKel = cur.fetchone()

        if hasilKel:
            id_kelurahan = hasilKel[0]
        else:
            query_insertLurah = """
                INSERT INTO kelurahan (nama_kelurahan, id_kecamatan)
                VALUES (%s, %s) RETURNING id_kelurahan
            """
            cur.execute(query_insertLurah, (lurah, id_kecamatan))
            id_kelurahan = cur.fetchone()[0]
            
        query_insertPet = """
            INSERT INTO petani_kopi (nama, no_telp, alamat, id_akun, id_kelurahan) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query_insertPet, (nama, no_telp, alamat, id_akun_baru, id_kelurahan))

        conn.commit()

        info("Akun Petani Baru Telah Ditambahkan!")

        pilihan = input("Tambah akun petani lain? [y/n]: ").lower()
        if pilihan == "y":
            continue
        elif pilihan == "n":
            break
        else:
            warn("Pilihan Invalid!")
        
        conn.close()
        return id_akun_baru

def delPetani():
    conn, cur = connectDB()
    while True:
        section_title("HAPUS AKUN PETANI")
        lihatAkunPetani()

        username = input("Masukkan Username Petani : ")
        query_akun = "SELECT id_akun FROM akun WHERE username = %s AND id_role = 2"
        cur.execute(query_akun, (username,))
        data = cur.fetchone()

        if not data:
            warn("Akun Petani Tidak Ditemukan!")
            return

        id_akun = data[0]

        query_dropPetani = "DELETE FROM petani_kopi WHERE id_akun = %s"
        cur.execute(query_dropPetani, (id_akun,))

        query_dropAkun = "DELETE FROM akun WHERE id_akun = %s"
        cur.execute(query_dropAkun, (id_akun,))

        conn.commit()
        info(f"Akun Petani {username} Telah Dihapus!")

        pilihan = input("Hapus akun petani lain? [y/n]: ").lower()
        if pilihan == "y":
            continue
        elif pilihan == "n":
            break
        else:
            warn("Pilihan Invalid!")

    conn.close()

def lihatDataHari():  # admin
    conn, cur = connectDB()
    query = """
        SELECT dh.id_harian,
               dh.tanggal_penanaman,
               dp.jenis_kopi,
               dh.deskripsi,
               dp.id_penanaman,
               dpt.id_petani
        FROM data_harian dh
        JOIN data_penanaman dp ON (dh.id_penanaman = dp.id_penanaman)
        JOIN detail_petani dpt ON (dp.id_penanaman = dpt.id_penanaman)
        ORDER BY id_harian ASC
    """
    cur.execute(query)
    data = cur.fetchall()

    if not data:
        print("\nBelum Ada Data Perkembangan Dari Petani\n")
        conn.close()
        return
    
    dataFrame = pd.DataFrame(
        data,
        columns=[
            "ID Harian",
            "Tanggal Penanaman",
            "Jenis Kopi",
            "Deskripsi",
            "ID Penanaman",
            "ID Petani"
        ]
    )

    print_df_kopi(dataFrame, "DATA HARIAN")
    conn.close()

def stokKopi():  # Admin, Petani, Pembeli
    conn, cur = connectDB()

    query = """
        SELECT k.id_kopi,
               jk.jenis_kopi,
               k.kualitas,
               k.harga,
               k.jumlah_stok,
               k.deskripsi
        FROM kopi k
        JOIN jenis_kopi jk ON (jk.id_jenis_kopi = k.id_jenis_kopi)
        ORDER BY id_kopi ASC
    """
    cur.execute(query)
    data = cur.fetchall()

    if not data:
        print("Stok kopi masih kosong.")
        conn.close()
        return

    dataFrame = pd.DataFrame(
        data,
        columns=[
            "ID Kopi",
            "Jenis Kopi",
            "Kualitas",
            "Harga",
            "Jumlah Stok",
            "Deskripsi"
        ]
    )

    print_df_kopi(dataFrame, "STOK KOPI TERSEDIA")
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

        section_title("DAFTAR PENGAJUAN STOK (STATUS: pending)")
        query_pending = """
            SELECT v.id_verifikasi, p.nama, v.status_verifikasi, v.tanggal_terverifikasi    
            FROM verifikasi v
            JOIN petani_kopi p ON v.id_petani = p.id_petani
            WHERE v.status_verifikasi = 'pending'
            ORDER BY v.id_verifikasi ASC
        """
        cur.execute(query_pending)
        rows = cur.fetchall()

        if not rows:
            print("Tidak ada pengajuan stok yang sedang pending.")
            conn.close()
            return

        # ====== TABEL PENDING (3 kolom) ======
        pending_for_table = [(r[0], r[1], r[2]) for r in rows]  # id_ver, nama, status
        df_pending = pd.DataFrame(
            pending_for_table,
            columns=["ID Verifikasi", "Nama Petani", "Status"]
        )
        print_df_kopi(df_pending, "DAFTAR PENGAJUAN STOK (PENDING)")

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
            SELECT v.id_verifikasi,
                   p.nama,
                   d.id_detail_verifikasi,
                   d.id_kopi,
                   jk.jenis_kopi,
                   d.kuantitas,
                   d.jenis_kopi_baru,
                   d.deskripsi_baru,
                   d.harga_baru,
                   d.kualitas_baru
            FROM detail_verifikasi d
            JOIN verifikasi v ON d.id_verifikasi = v.id_verifikasi
            JOIN petani_kopi p ON v.id_petani = p.id_petani
            LEFT JOIN kopi k ON k.id_kopi = d.id_kopi
            LEFT JOIN jenis_kopi jk ON (jk.id_jenis_kopi = k.id_jenis_kopi)
            WHERE v.id_verifikasi = %s;
        """
        cur.execute(query_detail, (pilih,))
        details = cur.fetchall()

        if not details:
            print("Data verifikasi tidak ditemukan.")
            conn.close()
            continue

        # ====== TABEL DETAIL (4 kolom: ID, Jenis Kopi, Tambah Stok, Oleh) ======
        detail_rows = []
        detail_kopi_lama = []
        for (id_ver, nama_petani, id_det, id_kopi, jenis_kopi_lama,
             qty, jenis_baru, desk_baru, harga_baru, kualitas_baru) in details:
            if id_kopi is not None:
                # kopi lama
                detail_kopi_lama.append({
                    "ID": id_kopi,
                    "Jenis Kopi": jenis_kopi_lama,
                    "Tambah Stok": f"+{qty}",
                    "Diajukan Oleh": nama_petani
                })
                df_detail = pd.DataFrame(detail_kopi_lama, columns=["ID","Jenis Kopi","Tambah Stok","Diajukan Oleh"])
                print_df_kopi(df_detail, "DETAIL PENGAJUAN STOK LAMA")
            else:
                # kopi baru → tampilkan jenis baru & stok awal
                detail_rows.append({
                    "Jenis Kopi": jenis_baru,
                    "Deskripsi" : desk_baru,
                    "Harga"     : harga_baru,
                    "Stok Awal": qty,
                    "Kualitas" : kualitas_baru,
                    "Diajukan Oleh": nama_petani
                })
                df_detail = pd.DataFrame(detail_rows, columns=["Jenis Kopi","Deskripsi","Harga","Stok Awal","Kualitas", "Diajukan Oleh"])
                print_df_kopi(df_detail, "DETAIL PENGAJUAN STOK BARU")


        
        # ====== TAMPILAN LAMA TETAP ADA (persis punyamu) ======
        print("\n=== DETAIL PENGAJUAN ===")

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
                        INSERT INTO jenis_kopi (jenis_kopi)
                        VALUES (%s)
                        RETURNING id_jenis_kopi
                    """, (jenis_baru,))
                    new_jenis_kopi = cur.fetchone()[0]

                    cur.execute("""
                        INSERT INTO kopi (id_jenis_kopi, deskripsi, harga, jumlah_stok, kualitas)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id_kopi
                    """, (new_jenis_kopi, desk_baru, harga_baru, qty, kualitas_baru))
                    new_id_kopi = cur.fetchone()[0]

                    cur.execute("""
                        UPDATE detail_verifikasi
                        SET id_kopi = %s
                        WHERE id_detail_verifikasi = %s
                    """, (new_id_kopi, id_det))

            cur.execute("""
                UPDATE verifikasi
                SET status_verifikasi = 'disetujui',
                    id_admin = %s,
                    tanggal_terverifikasi = CURRENT_DATE
                WHERE id_verifikasi = %s
            """, (id_admin, pilih))

            conn.commit()
            print("Pengajuan telah DISETUJUI. Stok kopi sudah diperbarui / kopi baru sudah dibuat.")

        elif keputusan == "n":
            cur.execute("""
                UPDATE verifikasi
                SET status_verifikasi = 'ditolak',
                    id_admin = %s,
                    tanggal_terverifikasi = CURRENT_DATE
                WHERE id_verifikasi = %s
            """, (id_admin, pilih))

            conn.commit()
            print("Pengajuan telah DITOLAK. Stok kopi tidak berubah.")

        else:
            print("Pilihan tidak valid. Tidak ada perubahan.")

        conn.close()

        lanjut = input("\nProses pengajuan lain? [y/n]: ").lower()
        if lanjut != "y":
            break

def feedback(id_admin):  # Admin
    conn, cur = connectDB()
    section_title("FEEDBACK ADMIN")
    lihatDataHari()
    
    id_data_harian   = input("Masukkan ID Data Harian : ")
    catatan_feedback = input("Masukkan Feedback       : ")

    query = """
        INSERT INTO feedback (id_admin, id_harian, tanggal_feedback, catatan_feedback)
        VALUES (%s, %s, CURRENT_DATE, %s)
        RETURNING id_feedback
    """

    cur.execute(query, (id_admin, id_data_harian, catatan_feedback))

    id_feedback_baru = cur.fetchone()[0]
    conn.commit()
    conn.close()

    info("Feedback berhasil dikirim!")
    print(f"ID Feedback : {id_feedback_baru}")

#################### PETANI ####################

def dataPenanaman(id_petani):
    conn, cur = connectDB()

    # menu pakai arrow
    pilihan = menu_kopi("INPUT DATA PENANAMAN", [
        "Pakai jenis kopi yang SUDAH ADA di tabel kopi",
        "Catat JENIS KOPI BARU (belum ada di tabel kopi)"
    ])

    jenis_kopi = input("Masukkan Jenis Kopi : ").title()
    tanggal_penanaman = input("Masukkan Tanggal Penanaman (YYYY-MM-DD) : ")
    kuantitas = int(input("Masukkan Kuantitas : "))   
    deskripsi = input("Masukkan Deskripsi : ")

    id_kopi = None

    query_insert = """INSERT INTO data_penanaman (jenis_kopi,tanggal_penanaman, kuantitas, deskripsi)
    VALUES (%s, %s, %s, %s) RETURNING id_penanaman"""
    
    cur.execute(query_insert, (jenis_kopi,tanggal_penanaman, kuantitas, deskripsi))
    id_penanaman = cur.fetchone()[0]

    if pilihan == 1:
        stokKopi()
        try:
            id_kopi = int(input("Masukkan ID Kopi : "))
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

        query_insertDet = """INSERT INTO detail_petani (id_petani, id_penanaman, id_kopi) 
        VALUES (%s, %s, %s)"""
        cur.execute(query_insertDet, (id_petani, id_penanaman, id_kopi))

    elif pilihan == 2:
        query_insertDet = """INSERT INTO detail_petani (id_petani, id_penanaman, id_kopi)
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

    section_title("INPUT DATA PERKEMBANGAN TANAMAN")
    lihatPenanaman(id_petani)

    id_penanaman = input("Masukkan ID Penanaman yang ingin ditambahkan perkembangan: ")

    query_check = """
        SELECT p.id_penanaman, dp.id_kopi
        FROM data_penanaman p
        JOIN detail_petani dp ON (p.id_penanaman = dp.id_penanaman)
        WHERE p.id_penanaman = %s AND dp.id_petani = %s
    """
    cur.execute(query_check, (id_penanaman, id_petani))
    if not cur.fetchone():
        print("ID penanaman tidak ditemukan atau bukan milik Anda!")
        conn.close()
        return
    
    deskripsi = input("Masukkan deskripsi perkembangan: ")
    tanggal   = datetime.now()
    
    query_insert = """
        INSERT INTO data_harian (id_penanaman, tanggal_penanaman, deskripsi)
        VALUES (%s, %s, %s)
    """
    cur.execute(query_insert, (id_penanaman, tanggal, deskripsi))

    conn.commit()
    conn.close()
    info("Perkembangan berhasil ditambahkan!")

def ajuStok():
    global current_user_id

    id_akun_petani = current_user_id
    id_petani = getPetaniIdByAkun(id_akun_petani)
    
    if id_petani is None:
        print("Data petani tidak ditemukan. Pastikan akun petani sudah terhubung.")
        return

    while True:
        # ===== MENU PAKAI ARROW =====
        pilihan = menu_kopi("PENGAJUAN STOK KOPI", [
            "Ajukan stok kopi yang SUDAH ADA",
            "Ajukan kopi JENIS BARU",
            "Kembali ke menu sebelumnya"
        ])

        # 1. Pengajuan stok kopi yang sudah ada
        if pilihan == 1:
            conn, cur = connectDB()
            section_title("PENGAJUAN STOK KOPI - KOPI LAMA")
            stokKopi()

            try:
                id_kopi = int(input("Masukkan ID Kopi yang ingin diajukan stoknya : "))
            except ValueError:
                print("ID kopi harus berupa angka!")
                conn.close()
                continue

            try:
                kuantitas = int(input("Masukkan jumlah stok yang diajukan : "))
            except ValueError:
                print("Kuantitas harus berupa angka!")
                conn.close()
                continue

            cur.execute(
                """
                SELECT j.jenis_kopi, k.id_kopi
                FROM jenis_kopi j
                JOIN kopi k ON j.id_jenis_kopi = k.id_jenis_kopi
                WHERE k.id_kopi = %s
                """,
                (id_kopi,)
            )
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
                INSERT INTO verifikasi (id_admin, id_petani, status_verifikasi, tanggal_terverifikasi)
                VALUES (NULL, %s, 'pending', NULL)
                RETURNING id_verifikasi
            """
            cur.execute(query_verifikasi, (id_petani,))
            id_verifikasi = cur.fetchone()[0]

            query_detail = """
                INSERT INTO detail_verifikasi (kuantitas, id_verifikasi, id_kopi)
                VALUES (%s, %s, %s)
            """
            cur.execute(query_detail, (kuantitas, id_verifikasi, id_kopi))

            conn.commit()
            conn.close()

            print(f"Pengajuan stok berhasil dikirim dengan ID verifikasi {id_verifikasi}.")
            print("Status: pending, menunggu persetujuan admin.\n")

        # 2. Pengajuan kopi jenis baru
        elif pilihan == 2:
            conn, cur = connectDB()

            section_title("PENGAJUAN KOPI JENIS BARU")
            jenis_kopi = input("Masukkan Jenis Kopi Baru   : ").capitalize()
            deskripsi  = input("Masukkan Deskripsi Kopi    : ")
            try:
                harga     = int(input("Masukkan Harga Kopi        : "))
                kuantitas = int(input("Masukkan Jumlah Stok Awal  : "))
            except ValueError:
                print("Harga dan kuantitas harus berupa angka!")
                conn.close()
                continue
            kualitas = input("Masukkan Kualitas Kopi     : ").capitalize()

            query_verifikasi = """
                INSERT INTO verifikasi (id_admin, id_petani, status_verifikasi, tanggal_terverifikasi)
                VALUES (NULL, %s, 'pending', NULL)
                RETURNING id_verifikasi
            """
            cur.execute(query_verifikasi, (id_petani,))
            id_verifikasi = cur.fetchone()[0]

            query_detail = """
                INSERT INTO detail_verifikasi (
                    kuantitas, id_verifikasi, id_kopi,
                    jenis_kopi_baru, deskripsi_baru, harga_baru, kualitas_baru
                )
                VALUES (%s, %s, NULL, %s, %s, %s, %s)
            """
            cur.execute(
                query_detail,
                (kuantitas, id_verifikasi, jenis_kopi, deskripsi, harga, kualitas)
            )

            conn.commit()
            conn.close()

            print(f"Pengajuan KOPI BARU berhasil dikirim dengan ID verifikasi {id_verifikasi}.")
            print("Status: pending, menunggu persetujuan admin.\n")

        # 3. Kembali ke menu sebelumnya
        elif pilihan == 3:
            break

        else:
            print("Pilihan tidak valid!")

        # tanya mau ajukan lagi atau tidak (boleh tetap pakai y/n biasa)
        lanjut = input("Ajukan lagi? [y/n]: ").lower()
        if lanjut != "y":
            break

def mail(id_petani):
    conn, cur = connectDB()
    query_select = """
        SELECT f.id_feedback,
               f.catatan_feedback,
               d.id_harian,
               d.deskripsi,
               d.tanggal_penanaman,
               dp.id_petani
        FROM feedback f
        JOIN data_harian d   ON (d.id_harian = f.id_harian)
        JOIN data_penanaman dm ON (dm.id_penanaman = d.id_penanaman)
        JOIN detail_petani dp   ON (dm.id_penanaman = dp.id_penanaman)
        WHERE dp.id_petani = %s
    """

    cur.execute(query_select, (id_petani,))
    hasil = cur.fetchall()

    section_title("FEEDBACK UNTUK DATA HARIAN ANDA")

    if not hasil:
        print("Belum ada feedback dari admin.")
        conn.close()
        return

    df = pd.DataFrame(
        hasil,
        columns=[
            "ID Feedback",
            "Catatan Feedback",
            "ID Harian",
            "Deskripsi",
            "Tanggal Penanaman",
            "ID Petani"
        ]
    )

    # TABEL PAKAI TEMA KOPI (kuning + teks putih), TANPA JUDUL KEDUA
    print_df_kopi(df)
    conn.close()

#################### PEMBELI ####################

def orderKopi():
    global current_user_id
    conn, cur = connectDB()

    section_title("ORDER KOPI")
    stokKopi()
    
    id_kopi = input("Masukkan ID Kopi : ")
    jumlah  = int(input("Masukkan Jumlah : "))
    cur.execute("""
        SELECT k.harga, k.jumlah_stok, jk.jenis_kopi
        FROM kopi k
        JOIN jenis_kopi jk ON k.id_jenis_kopi = jk.id_jenis_kopi
        WHERE id_kopi = %s
    """, (id_kopi,))
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

    status  = "Lunas"
    tanggal = datetime.now()

    query_insertOrders = """
        INSERT INTO orders (tanggal_order, id_transaksi, id_pembeli) 
        VALUES (%s, NULL, %s) RETURNING id_order
    """
    cur.execute(query_insertOrders, (tanggal, current_user_id))
    id_order = cur.fetchone()[0]

    query_updateKopi = "UPDATE kopi SET jumlah_stok = jumlah_stok - %s WHERE id_kopi = %s"
    cur.execute(query_updateKopi, (jumlah, id_kopi))

    query_insertDetOrd = """
        INSERT INTO detail_order (harga, kuantitas, id_order, id_kopi)
        VALUES (%s, %s, %s, %s)
    """
    cur.execute(query_insertDetOrd, (harga, jumlah, id_order, id_kopi))

    query_insertTransaksi = """
        INSERT INTO transaksi (tanggal_transaksi, status_pembayaran, id_order)
        VALUES (%s, %s, %s) RETURNING id_transaksi
    """   
    cur.execute(query_insertTransaksi, (tanggal, status, id_order))
    id_transaksi = cur.fetchone()[0]

    query_updateOrders = "UPDATE orders SET id_transaksi = %s WHERE id_order = %s"
    cur.execute(query_updateOrders, (id_transaksi, id_order))

    conn.commit()
    conn.close()
    info(f"Pembelian berhasil! Status pembayaran: {status} | Tanggal: {tanggal}")

def history():
    global current_user_id

    if current_user_id is None:
        print("Anda belum login!")
        return

    try:
        conn, cur = connectDB()

        query_select = """
            SELECT o.id_order,
                   k.id_kopi,
                   od.kuantitas,
                   od.harga,
                   o.tanggal_order,
                   t.status_pembayaran,
                   (od.harga * od.kuantitas) as total
            FROM detail_order od
            JOIN orders o    ON (o.id_order = od.id_order)
            JOIN kopi k      ON (k.id_kopi = od.id_kopi)
            JOIN transaksi t ON (t.id_transaksi = o.id_transaksi)
            WHERE o.id_pembeli = %s
            ORDER BY o.tanggal_order
        """
        cur.execute(query_select, (current_user_id,))
        data = cur.fetchall()
        conn.close()

        if not data:
            print("Riwayat pembelian masih kosong.")
            return

        # BUAT DATAFRAME & TAMPILKAN DENGAN TEMA KOPI
        df = pd.DataFrame(
            data,
            columns=[
                "ID Order",
                "ID Kopi",
                "Jumlah",
                "Harga",
                "Tanggal",
                "Status Bayar",
                "Total"
            ]
        )

        print_df_kopi(df, "RIWAYAT PEMBELIAN")

    except Exception as e:
        print("Gagal mengambil riwayat:", e)

def addKopi(tanggal_penanaman, deskripsi):
    conn, cur = connectDB()
    query_insert = "INSERT INTO data_penanaman(tanggal_penanaman, deskripsi) VALUES(%s, %s)"

    cur.execute(query_insert, (tanggal_penanaman, deskripsi))
    conn.commit()
    print('Data Telah ditambahkan')
    conn.close()

def addstokKopi():  # Admin
    while True:
        conn, cur = connectDB()
    
        section_title("TAMBAH / UPDATE STOK KOPI")
        stokKopi()
        id_kopi      = int(input("Masukkan ID Kopi         : "))
        jumlah_stok  = int(input("Masukkan Jumlah Stok     : "))
    
        query_select = "SELECT jumlah_stok FROM kopi WHERE id_kopi = %s"
        cur.execute(query_select, (id_kopi,))
        data = cur.fetchone()
    
        if data is None:
            print("Data Tidak Ditemukan!")
            pilihan = input("Apakah Anda Ingin Menambah Data Baru? [y/n]: ")

            if pilihan == "y":
                section_title("TAMBAH STOK BARU")

                jenis_kopi   = input("Masukkan Jenis Kopi Baru : ")
                nama_kopi    = input("Masukkan Nama Kopi       : ")
                deskripsi    = input("Masukkan Deskripsi Kopi  : ")
                harga        = int(input("Masukkan Harga Kopi      : "))
                jumlah_stok  = int(input("Masukkan Jumlah Stok     : "))
                kualitas     = input("Masukkan Kualitas Kopi   : ")

                query_insert = """
                    INSERT INTO kopi(jenis_kopi, nama_kopi, deskripsi, harga, jumlah_stok, kualitas)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(query_insert, (jenis_kopi, nama_kopi, deskripsi, harga, jumlah_stok, kualitas))
                conn.commit()
                print("Data Kopi Baru Telah Ditambah!")
                conn.close()

                pilihan = input("Apakah anda ingin melanjutkan menambah kopi? [y/n]: ").lower()
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
            
            id_kopi      = input("Masukkan ID Kopi        : ")
            jumlah_stok  = input("Masukkan Jumlah Stok    : ")

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

    query_select = """
        SELECT p.id_petani, p.nama, p.id_akun, a.username
        FROM petani_kopi p
        JOIN akun a ON (p.id_akun = a.id_akun)
        ORDER BY id_petani ASC
    """
    cur.execute(query_select)
    rows = cur.fetchall()

    if not rows:
        print("===DATA PETANI KOSONG===")
        return

    df = pd.DataFrame(
        rows,
        columns=["ID Petani", "Nama Petani", "ID Akun", "Username"]
    )
    print_df_kopi(df, "DATA PETANI")

    conn.close()

def lihatAkunAdmin():
    conn, cur = connectDB()

    query_select = """
        SELECT a.id_admin, a.nama, a.id_akun, ak.username
        FROM admins a
        JOIN akun ak ON (a.id_akun = ak.id_akun)
        ORDER BY id_admin ASC
    """
    cur.execute(query_select)
    rows = cur.fetchall()

    if not rows:
        print("===DATA ADMIN KOSONG===")
        return

    df = pd.DataFrame(
        rows,
        columns=["ID Admin", "Nama Admin", "ID Akun", "Username"]
    )
    print_df_kopi(df, "DATA ADMIN")

    conn.close()

def daRiPetani():  # Admin
    conn, cur = connectDB()

    query = """
        SELECT id_harian, id_penanaman, tanggal_penanaman, deskripsi
        FROM data_harian
        ORDER BY tanggal_penanaman ASC
    """
    cur.execute(query)
    data = cur.fetchall()

    if not data:
        print("Data Harian Petani masih kosong.")
        conn.close()
        return

    df = pd.DataFrame(
        data,
        columns=["ID Data Harian", "ID Penanaman", "Tanggal Penanaman", "Deskripsi"]
    )

    print_df_kopi(df, "DATA HARIAN PETANI")
    conn.close()

##################### MAIN (REGISTER / LOGIN / MENU) ####################

def mainRegister():
    conn, cur = connectDB()

    section_title("REGISTER PEMBELI")
    username = input("Masukkan username          : ")
    password = input("Masukkan password          : ")
    nama     = input("Masukkan nama              : ").title()
    alamat   = input("Masukkan alamat            : ").title()
    lurah    = input("Masukkan Kelurahan         : ").title()
    camat    = input("Masukkan Kecamatan         : ").title()
    no_telp  = input("Masukkan no telpon aktif   : ")

    query_insertAkun = """
        INSERT INTO akun (username, passwords, id_role)
        VALUES (%s, %s, 3) RETURNING id_akun
    """
    cur.execute(query_insertAkun, (username, password))
    id_akun_baru = cur.fetchone()[0]

    query_checkCamat = """
        SELECT id_kecamatan FROM kecamatan
        WHERE LOWER(nama_kecamatan) = LOWER(%s)
    """
    cur.execute(query_checkCamat, (camat,))
    hasil = cur.fetchone()

    if hasil:
        id_kecamatan = hasil[0]
    else:
        query_insertCamat = """
            INSERT INTO kecamatan (nama_kecamatan)
            VALUES (%s) RETURNING id_kecamatan
        """
        cur.execute(query_insertCamat, (camat,))
        id_kecamatan = cur.fetchone()[0]

    query_checkLurah = """
        SELECT id_kelurahan FROM kelurahan
        WHERE LOWER(nama_kelurahan) = LOWER(%s)
          AND id_kecamatan = %s
    """
    cur.execute(query_checkLurah, (lurah, id_kecamatan))
    hasilKel = cur.fetchone()

    if hasilKel:
        id_kelurahan = hasilKel[0]
    else:
        query_insertLurah = """
            INSERT INTO kelurahan (nama_kelurahan, id_kecamatan)
            VALUES (%s, %s) RETURNING id_kelurahan
        """
        cur.execute(query_insertLurah, (lurah, id_kecamatan))
        id_kelurahan = cur.fetchone()[0]
        
    query_insertPembeli = """
        INSERT INTO pembeli (nama, no_telp, alamat, id_akun, id_kelurahan)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(query_insertPembeli, (nama, no_telp, alamat, id_akun_baru, id_kelurahan))

    conn.commit()

    info("Berhasil Membuat Akun!")
    print(f"ID Akun : {id_akun_baru}")

    conn.close()

def mainLogin():
    global current_user_id
    global admins_id_admin
    conn, cur = connectDB()

    section_title("LOGIN")
    username = input("Masukkan username : ")
    password = input("Masukkan password : ")
    id_akun, _ = login(username, password)

    query_select = """
        SELECT a.id_akun, r.nama_role, p.id_pembeli
        FROM akun a
        JOIN roles r  ON a.id_role = r.id_role
        LEFT JOIN pembeli p ON p.id_akun = a.id_akun
        WHERE a.username = %s AND a.passwords = %s
    """

    cur.execute(query_select, (username, password))
    row = cur.fetchone()

    if not row:
        warn("Login gagal!")
        return False

    id_akun, role, id_pembeli = row

    if role == "pembeli":
        current_user_id = id_pembeli
    else:
        current_user_id = id_akun

    info(f"Login berhasil sebagai: {role}")

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
        pilihan = menu_kopi("MAIN ADMIN", [
            "Tambah Akun Admin",
            "Hapus Akun Admin",
            "Tambah Akun Petani",
            "Hapus Akun Petani",
            "Menampilkan Data Harian Petani",
            "Menampilkan Stok Kopi",
            "Verifikasi Pengajuan Stok Kopi",
            "Feedback",
            "LogOut"
        ])

        if pilihan == 1:
            addAdmin()
        elif pilihan == 2:
            delAdmin()
        elif pilihan == 3:
            addPetani()
        elif pilihan == 4:
            delPetani()
        elif pilihan == 5:
            lihatDataHari()
        elif pilihan == 6:
            stokKopi()
        elif pilihan == 7:
            verifikasiStok()
        elif pilihan == 8:
            feedback(id_admin)
        elif pilihan == 9:
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
        pilihan = menu_kopi("MAIN PETANI", [
            "Input Data Awal Penanaman",
            "Input Data Perkembangan Tanaman",
            "Mail Feedback",
            "Pengajuan Stok",
            "LogOut"
        ])

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
        pilihan = menu_kopi("MAIN PEMBELI", [
            "Tampilkan Stok Kopi",
            "Order Kopi",
            "History Pembelian",
            "LogOut"
        ])
        
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
    banner_komen()
    while True:
        pilihan = menu_kopi("MENU UTAMA", [
            "Register",
            "Login",
            "Keluar"
        ])

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
