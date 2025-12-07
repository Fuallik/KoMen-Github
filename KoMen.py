import psycopg2
import pandas as pd
from datetime import datetime
import os
import msvcrt
from tabulate import tabulate
import pyfiglet
from colorama import Fore,Back , Style, init

current_user_id = None

########### STYLES ##############

COFFEE      = Fore.YELLOW               
RESET       = Style.RESET_ALL           
HIGHLIGHT   = Back.YELLOW + Fore.BLUE + Style.BRIGHT 

TABLE_BORDER = Fore.CYAN                
TABLE_TEXT   = Fore.WHITE   

def menu_kopi(title: str, options: list[str]) -> int:
    try:
        selected = 0
        first_render = True

        total_lines = 1 + 1 + 1 + 1 + len(options) + 1 + 1

        print("\033[?25l", end="")

        try:
            while True:
                if not first_render:
                    print("\r\033[{}A".format(total_lines), end="")
                else:
                    first_render = False

                raw_lines = [opt for opt in options]
                lines = []
                for i, line in enumerate(raw_lines):
                    prefix = "▶" if i == selected else " "
                    lines.append(f"{prefix} {line}")

                max_len = max(len(line) for line in lines)
                width   = max(max_len, len(title)) + 4

                print() 

                print(COFFEE + "╭" + "─" * width + "╮" + RESET)
                print(
                    COFFEE + "│ " + RESET +
                    COFFEE + title.center(width-2) + RESET +
                    COFFEE + " │" + RESET
                )
                print(COFFEE + "├" + "─" * width + "┤" + RESET)

                for i, line in enumerate(lines):
                    if i == selected:
                        inner = HIGHLIGHT + COFFEE + line.ljust(width-2) + RESET
                    else:
                        inner = COFFEE + line.ljust(width-2) + RESET

                    print(
                        COFFEE + "│ " + RESET + inner +
                        COFFEE + " │" + RESET
                    )

                print(COFFEE + "╰" + "─" * width + "╯" + RESET)
                print("↑/↓ : pilih menu   Enter : OK", flush=True)

                key = msvcrt.getch()

                if key == b'\xe0':
                    key2 = msvcrt.getch()
                    if key2 == b'H':
                        selected = (selected - 1) % len(options)
                    elif key2 == b'P':
                        selected = (selected + 1) % len(options)

                elif key in (b'\r', b'\n'):
                    print()
                    os.system("cls" if os.name == "nt" else "clear")
                    return selected + 1

        finally:
            print("\033[?25h", end="")
    except Exception as e:
        print("Terjadi kesalahan di fungsi menu_kopi:", e)
        return 1


def yes_no_arrow(title: str) -> str:
    try:
        pilihan = menu_kopi(title, ["Ya", "Tidak"])
        return "y" if pilihan == 1 else "n"
    except Exception as e:
        print("Terjadi kesalahan di fungsi yes_no_arrow:", e)
        return "n"

init(autoreset=True)

TITLE = Fore.LIGHTYELLOW_EX + Style.BRIGHT
INFO  = Fore.LIGHTWHITE_EX
ERROR = Fore.LIGHTRED_EX

def input_kuning(prompt: str = "") -> str:
    try:
        return input(Fore.LIGHTYELLOW_EX + prompt + RESET)
    except Exception as e:
        print("Terjadi kesalahan saat input:", e)
        return ""


def banner_komen():
    try:
        os.system("cls")
        text = pyfiglet.figlet_format("KoMen", font="big")
        print(COFFEE + text + RESET)
    except Exception as e:
        print("Terjadi kesalahan di fungsi banner_komen:", e)


def section_title(text: str):
    try:
        bar = "─" * (len(text) + 2)
        print()
        print(COFFEE + f"╭{bar}╮")
        print(f"│ {text} │")
        print(f"╰{bar}╯" + RESET)
    except Exception as e:
        print("Terjadi kesalahan di fungsi section_title:", e)


def info(text: str):
    try:
        print(INFO + f"[i] {text}" + RESET)
    except Exception as e:
        print("Terjadi kesalahan di fungsi info:", e)


def warn(text: str):
    try:
        print(ERROR + f"[!] {text}" + RESET)
    except Exception as e:
        print("Terjadi kesalahan di fungsi warn:", e)


def status(text: str):
    try:
        print(Fore.LIGHTYELLOW_EX + text + RESET)
    except Exception as e:
        print("Terjadi kesalahan di fungsi status:", e)


def print_df_kopi(df: pd.DataFrame, title: str | None = None):
    try:
        if df is None or df.empty:
            print("Tabel kosong.")
            return

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
    except Exception as e:
        print("Terjadi kesalahan di fungsi print_df_kopi:", e)


########### DATABASE ##############

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
    except Exception as e:
        print("Koneksi gagal:", e)
        return None, None


def getPetaniIdByAkun(id_akun):
    try:
        conn, cur = connectDB()
        if conn is None:
            return None
        cur.execute("SELECT id_petani FROM petani_kopi WHERE id_akun = %s", (id_akun,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
    except Exception as e:
        print("Terjadi kesalahan di fungsi getPetaniIdByAkun:", e)
        return None


def getAdminIdByAkun(id_akun):
    try:
        conn, cur = connectDB()
        if conn is None:
            return None
        cur.execute("SELECT id_admin FROM admins WHERE id_akun = %s", (id_akun,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
    except Exception as e:
        print("Terjadi kesalahan di fungsi getAdminIdByAkun:", e)
        return None


def login(username, password):
    try:
        conn, cur = connectDB()
        if conn is None:
            return None, None
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi login:", e)
        return None, None

def lihatPenanaman(id_petani):
    try:
        conn, cur = connectDB()
        if conn is None:
            return
        query = """
            SELECT p.id_penanaman, p.jenis_kopi, p.kuantitas, p.tanggal_penanaman, p.deskripsi, d.id_petani FROM data_penanaman p
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi lihatPenanaman:", e)


#################### ADMIN ####################

def addAdmin():
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        while True:
            section_title("TAMBAH AKUN ADMIN")

            while True:
                username = input_kuning("Username Admin Baru  : ")
                if not username.strip():
                    warn("Username tidak boleh kosong!")
                    continue
                cur.execute("SELECT 1 FROM akun WHERE username = %s", (username,))
                if cur.fetchone():
                    warn("Username sudah digunakan, silakan gunakan username lain.")
                    continue
                break

            while True:
                pw = input_kuning("Password Admin Baru  : ")
                if not pw.strip():
                    warn("Password tidak boleh kosong!")
                    continue
                break

            while True:
                nama = input_kuning("Nama Admin Baru      : ").title()
                if not nama.strip():
                    warn("Nama admin tidak boleh kosong!")
                    continue
                break

            while True:
                no_telp = input_kuning("Nomor Telepon        : ")
                if not no_telp.strip():
                    warn("Nomor telepon tidak boleh kosong!")
                    continue
                if not no_telp.isdigit():
                    warn("Nomor telepon harus berupa angka!")
                    continue
                break

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

            pilihan = yes_no_arrow("Tambah akun admin lain?")
            if pilihan == "y":
                continue
            elif pilihan == "n":
                break
            else:
                warn("Pilihan Invalid!")
            
            conn.close()
            return id_akun_baru

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi addAdmin:", e)


def delAdmin():
    try:
        conn, cur = connectDB()
        if conn is None:
            return
        while True:
            section_title("HAPUS AKUN ADMIN")
            lihatAkunAdmin()

            username = input_kuning("Masukkan Username Admin : ")
            query_akun = "SELECT id_akun FROM akun WHERE username = %s AND id_role = 1"
            cur.execute(query_akun, (username,))
            data = cur.fetchone()

            if not data:
                warn("Akun Admin Tidak Ditemukan!")
                conn.close()
                return

            id_akun = data[0]

            query_dropAdmin = "DELETE FROM admins WHERE id_akun = %s"
            cur.execute(query_dropAdmin, (id_akun,))

            query_dropAkun = "DELETE FROM akun WHERE id_akun = %s"
            cur.execute(query_dropAkun, (id_akun,))

            conn.commit()
            info(f"Akun Admin {username} Telah Dihapus!")

            pilihan = yes_no_arrow("Hapus akun admin lain?")
            if pilihan == "y":
                continue
            elif pilihan == "n":
                break
            else:
                warn("Pilihan Invalid!")

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi delAdmin:", e)


def addPetani():
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        while True:
            section_title("TAMBAH AKUN PETANI")

            while True:
                username = input_kuning("Masukkan Username Petani Baru : ")
                if not username.strip():
                    warn("Username tidak boleh kosong!")
                    continue
                cur.execute("SELECT 1 FROM akun WHERE username = %s", (username,))
                if cur.fetchone():
                    warn("Username sudah digunakan, silakan gunakan username lain.")
                    continue
                break

            while True:
                pw = input_kuning("Masukkan Password Petani Baru : ")
                if not pw.strip():
                    warn("Password tidak boleh kosong!")
                    continue
                break

            while True:
                nama = input_kuning("Masukkan Nama Petani Baru     : ").title()
                if not nama.strip():
                    warn("Nama petani tidak boleh kosong!")
                    continue
                break

            while True:
                alamat = input_kuning("Masukkan Alamat Petani Baru   : ").title()
                if not alamat.strip():
                    warn("Alamat tidak boleh kosong!")
                    continue
                break

            while True:
                lurah = input_kuning("Masukkan Kelurahan Petani     : ").title()
                if not lurah.strip():
                    warn("Kelurahan tidak boleh kosong!")
                    continue
                break

            while True:
                camat = input_kuning("Masukkan Kecamatan Petani     : ").title()
                if not camat.strip():
                    warn("Kecamatan tidak boleh kosong!")
                    continue
                break

            while True: 
                no_telp = input_kuning("Masukkan Nomor Telepon        : ")
                if not no_telp.strip():
                    warn("Nomor telepon tidak boleh kosong!")
                    continue
                if not no_telp.isdigit():
                    warn("Nomor telepon harus berupa angka!")
                    continue
                break

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

            pilihan = yes_no_arrow("Tambah akun petani lain?")
            if pilihan == "y":
                continue
            elif pilihan == "n":
                break
            else:
                warn("Pilihan Invalid!")
            
            conn.close()
            return id_akun_baru

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi addPetani:", e)


def delPetani():
    try:
        conn, cur = connectDB()
        if conn is None:
            return
        while True:
            section_title("HAPUS AKUN PETANI")
            lihatAkunPetani()

            username = input_kuning("Masukkan Username Petani : ")
            query_akun = "SELECT id_akun FROM akun WHERE username = %s AND id_role = 2"
            cur.execute(query_akun, (username,))
            data = cur.fetchone()

            if not data:
                warn("Akun Petani Tidak Ditemukan!")
                conn.close()
                return

            id_akun = data[0]

            query_dropPetani = "DELETE FROM petani_kopi WHERE id_akun = %s"
            cur.execute(query_dropPetani, (id_akun,))

            query_dropAkun = "DELETE FROM akun WHERE id_akun = %s"
            cur.execute(query_dropAkun, (id_akun,))

            conn.commit()
            info(f"Akun Petani {username} Telah Dihapus!")

            pilihan = yes_no_arrow("Hapus akun petani lain?")
            if pilihan == "y":
                continue
            elif pilihan == "n":
                break
            else:
                warn("Pilihan Invalid!")

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi delPetani:", e)


def lihatDataHari():
    try:
        conn, cur = connectDB()
        if conn is None:
            return
        query = """
            SELECT dh.id_harian ,dh.tanggal_penanaman, dp.jenis_kopi, dh.deskripsi, dp.id_penanaman, dpt.id_petani FROM data_harian dh
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi lihatDataHari:", e)


def stokKopi():
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        query = """
            SELECT k.id_kopi, jk.jenis_kopi, k.kualitas, k.harga, k.jumlah_stok, k.deskripsi
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

        dataFrame = pd.DataFrame(data, columns=["ID Kopi", "Jenis Kopi", "Kualitas", "Harga", "Jumlah Stok", "Deskripsi"])

        print_df_kopi(dataFrame, "STOK KOPI TERSEDIA")
        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi stokKopi:", e)


def verifikasiStok():
    global current_user_id

    try:
        id_akun_admin = current_user_id
        id_admin = getAdminIdByAkun(id_akun_admin)

        if id_admin is None:
            print("Data admin tidak ditemukan. Pastikan akun admin sudah terhubung.")
            return

        while True:
            conn, cur = connectDB()
            if conn is None:
                return

            query_pending = """
                SELECT v.id_verifikasi, p.nama, v.status_verifikasi, v.tanggal_terverifikasi FROM verifikasi v
                JOIN petani_kopi p ON v.id_petani = p.id_petani
                WHERE v.status_verifikasi = 'pending'
                ORDER BY v.id_verifikasi ASC
            """
            cur.execute(query_pending)
            rows = cur.fetchall()

            if not rows:
                status("Tidak ada pengajuan stok yang sedang pending.")
                conn.close()
                return

            pending_for_table = [(r[0], r[1], r[2]) for r in rows] 
            df_pending = pd.DataFrame(
                pending_for_table,
                columns=["ID Verifikasi", "Nama Petani", "Status"]
            )
            print_df_kopi(df_pending, "DAFTAR PENGAJUAN STOK (PENDING)")

            try:
                pilih = int(input_kuning("\nMasukkan ID verifikasi yang ingin diproses (0 untuk kembali): "))
            except ValueError as e:
                print("Input tidak valid:", e)
                conn.close()
                continue

            if pilih == 0:
                conn.close()
                break
            
            query_detail = """
                SELECT v.id_verifikasi, p.nama, d.id_detail_verifikasi, d.id_kopi, jk.jenis_kopi, d.kuantitas, d.jenis_kopi_baru, d.deskripsi_baru, d.harga_baru, d.kualitas_baru FROM detail_verifikasi d
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

            detail_rows = []
            detail_kopi_lama = []
            for (id_ver, nama_petani, id_det, id_kopi, jenis_kopi_lama, qty, jenis_baru, desk_baru, harga_baru, kualitas_baru) in details:
                if id_kopi is not None:
                    detail_kopi_lama.append({
                        "ID": id_kopi,
                        "Jenis Kopi": jenis_kopi_lama,
                        "Tambah Stok": f"+{qty}",
                        "Diajukan Oleh": nama_petani
                    })
                    df_detail = pd.DataFrame(detail_kopi_lama, columns=["ID","Jenis Kopi","Tambah Stok","Diajukan Oleh"])
                    print_df_kopi(df_detail, "DETAIL PENGAJUAN STOK KOPI LAMA")
                else:
                    detail_rows.append({
                        "Jenis Kopi": jenis_baru,
                        "Deskripsi" : desk_baru,
                        "Harga"     : harga_baru,
                        "Stok Awal": qty,
                        "Kualitas" : kualitas_baru,
                        "Diajukan Oleh": nama_petani
                    })
                    df_detail = pd.DataFrame(detail_rows, columns=["Jenis Kopi","Deskripsi","Harga","Stok Awal","Kualitas", "Diajukan Oleh"])
                    print_df_kopi(df_detail, "DETAIL PENGAJUAN STOK KOPI BARU")

            print("\n=== DETAIL PENGAJUAN ===")

            keputusan = yes_no_arrow("Setujui pengajuan ini?")
            if keputusan == "y":
                for (id_ver, nama_petani, id_det, id_kopi, jenis_kopi_lama, qty, jenis_baru, desk_baru, harga_baru, kualitas_baru) in details:

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
                status("Pengajuan telah DISETUJUI. Stok kopi sudah diperbarui / kopi baru sudah dibuat.")

            elif keputusan == "n":
                cur.execute("""
                    UPDATE verifikasi
                    SET status_verifikasi = 'ditolak',
                        id_admin = %s,
                        tanggal_terverifikasi = CURRENT_DATE
                    WHERE id_verifikasi = %s
                """, (id_admin, pilih))

                conn.commit()
                status("Pengajuan telah DITOLAK. Stok kopi tidak berubah.")

            else:
                status("Pilihan tidak valid. Tidak ada perubahan.")

            conn.close()

            lanjut = yes_no_arrow("Proses pengajuan lain?")
            if lanjut != "y":
                break
    except Exception as e:
        print("Terjadi kesalahan di fungsi verifikasiStok:", e)


def feedback(id_admin):
    try:
        conn, cur = connectDB()
        if conn is None:
            return
        section_title("FEEDBACK ADMIN")
        lihatDataHari()
        
        id_data_harian   = input_kuning("Masukkan ID Data Harian : ")
        catatan_feedback = input_kuning("Masukkan Feedback       : ")

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
    except Exception as e:
        print("Telah keluar dari feedback")


#################### PETANI ####################

def dataPenanaman(id_petani):
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        pilihan = menu_kopi("INPUT DATA PENANAMAN", [
            "Pakai jenis kopi yang SUDAH ADA di tabel kopi",
            "Catat JENIS KOPI BARU (belum ada di tabel kopi)"
        ])
        while True:
            jenis_kopi = input_kuning("Masukkan Jenis Kopi : ").title()
            if not jenis_kopi.strip():
                warn("Jenis Kopi tidak boleh kosong!")
                continue
            break

        while True:
            tanggal_penanaman = input_kuning("Masukkan Tanggal Penanaman (YYYY-MM-DD) : ")
            try:
                datetime.strptime(tanggal_penanaman, "%Y-%m-%d")
                break
            except ValueError:
                warn("Format tanggal salah! Gunakan format YYYY-MM-DD, contoh: 2025-12-31.")

        while True:
            try:
                kuantitas = int(input_kuning("Masukkan Kuantitas : "))
            except ValueError:
                warn("Kuantitas harus berupa angka!")
                continue
            break

        while True:
            deskripsi = input_kuning("Masukkan Deskripsi : ")
            if not deskripsi.strip():
                warn("Deskripsi tidak boleh kosong!")
                continue
            break

        id_kopi = None

        query_insert = """INSERT INTO data_penanaman (jenis_kopi,tanggal_penanaman, kuantitas, deskripsi)
        VALUES (%s, %s, %s, %s) RETURNING id_penanaman"""
        
        cur.execute(query_insert, (jenis_kopi, tanggal_penanaman, kuantitas, deskripsi))
        id_penanaman = cur.fetchone()[0]

        if pilihan == 1:
            stokKopi()
            try:
                id_kopi = int(input_kuning("Masukkan ID Kopi : "))
            except ValueError as e:
                print("ID kopi harus berupa angka!", e)
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi dataPenanaman:", e)


def dataHari(id_petani):
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        section_title("INPUT DATA PERKEMBANGAN TANAMAN")
        lihatPenanaman(id_petani)

        while True:
            id_penanaman = input_kuning("Masukkan ID Penanaman yang ingin ditambahkan perkembangan: ")
            if not id_penanaman.strip():
                warn("ID Penanaman tidak boleh kosong!")
                continue
            if not id_penanaman.isdigit():
                warn("ID Penanaman harus berupa angka!")
                continue
            break

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
        
        while True:
            deskripsi = input_kuning("Masukkan Deskripsi Perkembangan : ")
            if not deskripsi.strip():
                warn("Deskripsi tidak boleh kosong!")
                continue
            break
        tanggal   = datetime.now()
        
        query_insert = """
            INSERT INTO data_harian (id_penanaman, tanggal_penanaman, deskripsi)
            VALUES (%s, %s, %s)
        """
        cur.execute(query_insert, (id_penanaman, tanggal, deskripsi))

        conn.commit()
        conn.close()
        info("Perkembangan berhasil ditambahkan!")
    except Exception as e:
        print("Terjadi kesalahan di fungsi dataHari:", e)


def ajuStok():
    global current_user_id

    try:
        id_akun_petani = current_user_id
        id_petani = getPetaniIdByAkun(id_akun_petani)
        
        if id_petani is None:
            print("Data petani tidak ditemukan. Pastikan akun petani sudah terhubung.")
            return

        while True:
            pilihan = menu_kopi("PENGAJUAN STOK KOPI", [
                "Ajukan stok kopi yang SUDAH ADA",
                "Ajukan kopi JENIS BARU",
                "Kembali ke menu sebelumnya"
            ])

            if pilihan == 1:
                conn, cur = connectDB()
                if conn is None:
                    return
                section_title("PENGAJUAN STOK KOPI LAMA")
                stokKopi()

                try:
                    id_kopi = int(input_kuning("Masukkan ID Kopi yang ingin diajukan stoknya : "))
                except ValueError as e:
                    print("ID kopi harus berupa angka dan tidak boleh kosong!")
                    conn.close()
                    continue

                try:
                    kuantitas = int(input_kuning("Masukkan jumlah stok yang diajukan : "))
                except ValueError as e:
                    print("Kuantitas harus berupa angka dan tidak boleh kosong!", e)
                    conn.close()
                    continue

                cur.execute(
                    """
                    SELECT j.jenis_kopi, k.id_kopi FROM jenis_kopi j
                    JOIN kopi k ON j.id_jenis_kopi = k.id_jenis_kopi
                    WHERE k.id_kopi = %s
                    """,
                    (id_kopi,)
                )
                row = cur.fetchone()
                if not row:
                    print("ID kopi tidak ditemukan!")
                    conn.close()
                    lanjut = yes_no_arrow("Ajukan pengajuan lagi?")
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

            elif pilihan == 2:
                conn, cur = connectDB()
                if conn is None:
                    return

                section_title("PENGAJUAN KOPI JENIS BARU")
                while True:
                    jenis_kopi = input_kuning("Masukkan Jenis Kopi Baru   : ").capitalize()
                    if not jenis_kopi.strip():
                        warn("Jenis Kopi Baru tidak boleh kosong!")
                        continue
                    break
                while True:
                    deskripsi  = input_kuning("Masukkan Deskripsi Kopi    : ")
                    if not deskripsi.strip():
                        warn("Deskripsi Kopi tidak boleh kosong!")
                        continue
                    break
                try:
                    harga     = int(input_kuning("Masukkan Harga Kopi        : "))
                    kuantitas = int(input_kuning("Masukkan Jumlah Stok Awal  : "))
                except ValueError as e:
                    print("Harga dan Jumlah Stok Awal harus berupa angka dan tidak boleh kosong!", e)
                    conn.close()
                    continue
                kualitas = input_kuning("Masukkan Kualitas Kopi     : ").capitalize()
                while kualitas not in ("A", "B", "C"):
                    warn("Kualitas hanya boleh A, B, atau C")
                    kualitas = input_kuning("Masukkan Kualitas Kopi (A-C)     : ").upper()

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

            elif pilihan == 3:
                break

            else:
                print("Pilihan tidak valid!")

            lanjut = yes_no_arrow("Ajukan pengajuan lagi?")
            if lanjut != "y":
                break
    except Exception as e:
        print("Terjadi kesalahan di fungsi ajuStok:", e)


def mail(id_petani):
    try:
        conn, cur = connectDB()
        if conn is None:
            return
        query_select = """
            SELECT f.id_feedback, f.catatan_feedback, d.id_harian, d.deskripsi, d.tanggal_penanaman, dp.id_petani FROM feedback f
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

        print_df_kopi(df)
        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi mail:", e)


#################### PEMBELI ####################

def orderKopi():
    global current_user_id
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        section_title("ORDER KOPI")
        stokKopi()
        while True:
            id_kopi = input_kuning("Masukkan ID Kopi : ")
            if not id_kopi.strip():
                warn("ID Kopi tidak boleh kosong!")
                continue
            break
        try:
            jumlah  = int(input_kuning("Masukkan Jumlah : "))
        except ValueError as e:
            print("Jumlah harus berupa angka dan tidak boleh kosong!", e)
            conn.close()
            return

        cur.execute("""
            SELECT k.harga, k.jumlah_stok, jk.jenis_kopi FROM kopi k
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

        konfirmasi = yes_no_arrow("Lanjutkan pembayaran?")
        if konfirmasi != "y":
            print("Pembayaran dibatalkan.")
            conn.close()
            return

        status_pembayaran  = "Lunas"
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
        cur.execute(query_insertTransaksi, (tanggal, status_pembayaran, id_order))
        id_transaksi = cur.fetchone()[0]

        query_updateOrders = "UPDATE orders SET id_transaksi = %s WHERE id_order = %s"
        cur.execute(query_updateOrders, (id_transaksi, id_order))

        conn.commit()
        conn.close()
        info(f"Pembelian berhasil! Status pembayaran: {status_pembayaran} | Tanggal: {tanggal}")
    except Exception as e:
        print("Terjadi kesalahan di fungsi orderKopi:", e)

def history():
    global current_user_id

    if current_user_id is None:
        print("Anda belum login!")
        return

    try:
        conn, cur = connectDB()
        if conn is None:
            return

        query_select = ("""
            SELECT o.id_order, k.id_kopi, od.kuantitas, od.harga, o.tanggal_order, t.status_pembayaran, (od.harga * od.kuantitas) as total FROM detail_order od
            JOIN orders o    ON (o.id_order = od.id_order)
            JOIN kopi k      ON (k.id_kopi = od.id_kopi)
            JOIN transaksi t ON (t.id_transaksi = o.id_transaksi)
            WHERE o.id_pembeli = %s
            ORDER BY o.tanggal_order
        """)
        cur.execute(query_select, (current_user_id,))
        data = cur.fetchall()
        conn.close()

        if not data:
            print("Riwayat pembelian masih kosong.")
            return

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

def lihatAkunPetani():
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        query_select = """
            SELECT p.id_petani, p.nama, p.id_akun, a.username FROM petani_kopi p JOIN akun a ON (p.id_akun = a.id_akun)
            ORDER BY id_petani ASC
        """
        cur.execute(query_select)
        rows = cur.fetchall()

        if not rows:
            print("===DATA PETANI KOSONG===")
            conn.close()
            return

        df = pd.DataFrame(
            rows,
            columns=["ID Petani", "Nama Petani", "ID Akun", "Username"]
        )
        print_df_kopi(df, "DATA PETANI")

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi lihatAkunPetani:", e)


def lihatAkunAdmin():
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        query_select = "SELECT a.id_admin, a.nama, a.id_akun, ak.username FROM admins a JOIN akun ak ON (a.id_akun = ak.id_akun) ORDER BY id_admin ASC"
        cur.execute(query_select)
        rows = cur.fetchall()

        if not rows:
            print("===DATA ADMIN KOSONG===")
            conn.close()
            return

        df = pd.DataFrame(
            rows,
            columns=["ID Admin", "Nama Admin", "ID Akun", "Username"]
        )
        print_df_kopi(df, "DATA ADMIN")

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi lihatAkunAdmin:", e)

##################### MAIN (REGISTER / LOGIN / MENU) ####################

def mainRegister():
    try:
        conn, cur = connectDB()
        if conn is None:
            return

        section_title("REGISTER PEMBELI")

        while True:
            username = input_kuning("Masukkan username          : ")
            cur.execute("SELECT 1 FROM akun WHERE username = %s", (username,))
            if not username.strip():
                warn("Username tidak boleh kosong!")
                continue
            if cur.fetchone():
                warn("Username sudah digunakan, silakan gunakan username lain.")
                continue
            break
            

        while True:
            password = input_kuning("Masukkan password          : ")
            if not password.strip():
                warn("Password tidak boleh kosong!")
                continue
            break

        while True:
            nama = input_kuning("Masukkan nama              : ").title()
            if not nama.strip():
                warn("Nama tidak boleh kosong!")
                continue
            break

        while True:
            alamat = input_kuning("Masukkan alamat            : ").title()
            if not alamat.strip():
                warn("Alamat tidak boleh kosong!")
                continue
            break

        while True:
            lurah = input_kuning("Masukkan Kelurahan         : ").title()
            if not lurah.strip():
                warn("Kelurahan tidak boleh kosong!")
                continue
            break

        while True:
            camat = input_kuning("Masukkan Kecamatan         : ").title()
            if not camat.strip():
                warn("Kecamatan tidak boleh kosong!")
                continue
            break

        while True:
            no_telp = input_kuning("Masukkan no telpon aktif   : ")
            if not no_telp.strip():
                warn("Nomor telepon tidak boleh kosong!")
                continue
            if not no_telp.isdigit():
                    warn("Nomor telepon harus berupa angka!")
                    continue
            break

        cur.execute("SELECT 1 FROM akun WHERE username = %s", (username,))
        if cur.fetchone():
            warn("Username sudah digunakan, silakan gunakan username lain.")
            conn.close()
            return

        query_insertAkun = " INSERT INTO akun (username, passwords, id_role) VALUES (%s, %s, 3) RETURNING id_akun"
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
            query_insertCamat = "INSERT INTO kecamatan (nama_kecamatan) VALUES (%s) RETURNING id_kecamatan"
            cur.execute(query_insertCamat, (camat,))
            id_kecamatan = cur.fetchone()[0]

        query_checkLurah = """
            SELECT id_kelurahan FROM kelurahan
            WHERE LOWER(nama_kelurahan) = LOWER(%s) AND id_kecamatan = %s
        """
        cur.execute(query_checkLurah, (lurah, id_kecamatan))
        hasilKel = cur.fetchone()

        if hasilKel:
            id_kelurahan = hasilKel[0]
        else:
            query_insertLurah = "INSERT INTO kelurahan (nama_kelurahan, id_kecamatan) VALUES (%s, %s) RETURNING id_kelurahan"
            cur.execute(query_insertLurah, (lurah, id_kecamatan))
            id_kelurahan = cur.fetchone()[0]
            
        query_insertPembeli = "INSERT INTO pembeli (nama, no_telp, alamat, id_akun, id_kelurahan) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(query_insertPembeli, (nama, no_telp, alamat, id_akun_baru, id_kelurahan))

        conn.commit()

        info("Berhasil Membuat Akun!")
        print(f"ID Akun : {id_akun_baru}")

        conn.close()
    except Exception as e:
        print("Terjadi kesalahan di fungsi mainRegister:", e)


def mainLogin():
    global current_user_id
    global admins_id_admin
    try:
        conn, cur = connectDB()
        if conn is None:
            return False

        section_title("LOGIN")
        while True:
            username = input_kuning("Masukkan username : ")
            if not username.strip():
                warn("Username tidak boleh kosong!")
                continue
            password = input_kuning("Masukkan password : ")
            if not password.strip():
                warn("Password tidak boleh kosong!")
                continue
            break
        id_akun_login, _ = login(username, password)

        query_select = """
            SELECT a.id_akun, r.nama_role, p.id_pembeli FROM akun a
            JOIN roles r  ON a.id_role = r.id_role
            LEFT JOIN pembeli p ON p.id_akun = a.id_akun
            WHERE a.username = %s AND a.passwords = %s
        """

        cur.execute(query_select, (username, password))
        row = cur.fetchone()

        if not row:
            warn("Login gagal!")
            conn.close()
            return False

        id_akun, role, id_pembeli = row

        if role == "pembeli":
            current_user_id = id_pembeli
        else:
            current_user_id = id_akun

        info(f"Login berhasil sebagai: {role}")

        if role == "admin":
            print("Anda login sebagai admin")
            conn.close()
            mainAdmin()
        elif role == "petani":
            print("Anda login sebagai petani")
            conn.close()
            mainPetani()
        elif role == "pembeli":
            print("Anda login sebagai pembeli")
            conn.close()
            mainPembeli()
        else:
            print("ERROR: Role tidak diketahui")
            conn.close()
        return True
    except Exception as e:
        print("Terjadi kesalahan di fungsi mainLogin:", e)
        return False


def mainAdmin():
    global current_user_id

    try:
        print("\033[?25l", end="")

        os.system('cls')
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi mainAdmin:", e)

def mainPetani():
    global current_user_id

    try:
        print("\033[?25l", end="")

        os.system('cls')
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi mainPetani:", e)


def mainPembeli():
    try:
        print("\033[?25l", end="")

        os.system('cls')
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi mainPembeli:", e)


def KoMen():
    try:
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
    except Exception as e:
        print("Terjadi kesalahan di fungsi KoMen:", e)

KoMen()