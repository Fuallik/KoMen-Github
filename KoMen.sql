-- ROLES
CREATE TABLE roles (
    id_role SERIAL PRIMARY KEY,
    nama_role VARCHAR(20) NOT NULL
);

-- AKUN
CREATE TABLE akun (
    id_akun SERIAL PRIMARY KEY,
    role_id_role INT NOT NULL REFERENCES roles(id_role),
    username VARCHAR(50) NOT NULL,
    passwords VARCHAR(50) NOT NULL
);

-- ADMINS
CREATE TABLE admins (
    id_admin SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    akun_id_akun INT NOT NULL REFERENCES akun(id_akun)
);

-- PEMBELI
CREATE TABLE pembeli (
    id_pembeli SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    alamat VARCHAR(50) NOT NULL,
    akun_id_akun INT NOT NULL REFERENCES akun(id_akun)
);

-- PETANI KOPI
CREATE TABLE petani_kopi (
    id_petani SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    alamat VARCHAR(50) NOT NULL,
    akun_id_akun INT NOT NULL REFERENCES akun(id_akun)
);

-- KOPI
CREATE TABLE kopi (
    id_kopi SERIAL PRIMARY KEY,
    jenis_kopi VARCHAR(50) NOT NULL,
    deskripsi TEXT NOT NULL,
    harga INT NOT NULL,
    jumlah_stok INT NOT NULL,
    kualitas VARCHAR(1) NOT NULL
);

-- DATA PENANAMAN
CREATE TABLE data_penanaman (
    id_penanaman SERIAL PRIMARY KEY,
    tanggal_penanaman DATE NOT NULL,
    deskripsi TEXT NOT NULL,
    jenis_kopi VARCHAR(50),
    kuantitas INT
);

-- DATA HARIAN
CREATE TABLE data_harian (
    id_harian SERIAL PRIMARY KEY,
    data_penanaman_id_penanaman INT NOT NULL REFERENCES data_penanaman(id_penanaman),
    tanggal_penanaman DATE NOT NULL,
    deskripsi TEXT NOT NULL
);

-- ORDERS
CREATE TABLE orders (
    id_order SERIAL PRIMARY KEY,
    tanggal_order DATE NOT NULL,
    transaksi_id_transaksi INT,          -- FK ditambah belakangan (karena hubungan saling referensi)
    pembeli_id_pembeli INT NOT NULL REFERENCES pembeli(id_pembeli)
);

-- TRANSAKSI
CREATE TABLE transaksi (
    id_transaksi SERIAL PRIMARY KEY,
    tanggal_transaksi DATE NOT NULL,
    status_pembayaran VARCHAR(20) NOT NULL,
    orders_id_order INT NOT NULL         -- FK ditambah belakangan (karena hubungan saling referensi)
);

-- DETAIL ORDER
CREATE TABLE order_detail (
    id_detail_order SERIAL PRIMARY KEY,
    harga INT NOT NULL,
    kuantitas INT NOT NULL,
    orders_id_order INT NOT NULL REFERENCES orders(id_order),
    kopi_id_kopi INT NOT NULL REFERENCES kopi(id_kopi)
);

-- VERIFIKASI
CREATE TABLE verifikasi (
    id_verifikasi SERIAL PRIMARY KEY,
    admins_id_admin INT REFERENCES admins(id_admin),
    petani_kopi_id_petani INT NOT NULL REFERENCES petani_kopi(id_petani),
    tanggal_terverifikasi DATE
);

-- DETAIL VERIFIKASI
CREATE TABLE detail_verifikasi (
    id_detail_verifikasi SERIAL PRIMARY KEY,
    kuantitas INT NOT NULL,
    verifikasi_id_verifikasi INT NOT NULL REFERENCES verifikasi(id_verifikasi),
    kopi_id_kopi INT REFERENCES kopi(id_kopi),
    jenis_kopi_baru VARCHAR(100),
    deskripsi_baru TEXT,
    harga_baru INT,
    kualitas_baru VARCHAR(1)
);

-- FEEDBACK
CREATE TABLE feedback (
    id_feedback SERIAL PRIMARY KEY,
    admins_id_admin INT NOT NULL REFERENCES admins(id_admin),
    data_harian_id_harian INT NOT NULL REFERENCES data_harian(id_harian),
    tanggal_feedback DATE NOT NULL,
    catatan_feedback TEXT NOT NULL
);

-- DETAIL PETANI
CREATE TABLE detail_petani (
    id_detail_petani SERIAL PRIMARY KEY,
    petani_kopi_id_petani INT NOT NULL REFERENCES petani_kopi(id_petani),
    data_penanaman_id_penanaman INT NOT NULL REFERENCES data_penanaman(id_penanaman),
    kopi_id_kopi INT REFERENCES kopi(id_kopi)
);

-- ========================
-- FOREIGN KEY BIKIN BELAKANGAN UNTUK RELASI MELINGKAR
-- ========================

ALTER TABLE orders
    ADD CONSTRAINT fk_orders_transaksi
    FOREIGN KEY (transaksi_id_transaksi)
    REFERENCES transaksi(id_transaksi);

ALTER TABLE transaksi
    ADD CONSTRAINT fk_transaksi_orders
    FOREIGN KEY (orders_id_order)
    REFERENCES orders(id_order);

INSERT INTO roles (nama_role) VALUES
('admin'),
('petani'),
('pembeli')

INSERT INTO akun (role_id_role, username, passwords)
VALUES (1, 'admin', '123')
RETURNING id_akun;

INSERT INTO admins (nama, no_telp, akun_id_akun)
VALUES ('Budi', '08123456789',1);
