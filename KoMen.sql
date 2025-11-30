-- TABLE: roles
CREATE TABLE roles (
    id_role SERIAL PRIMARY KEY,
    nama_role VARCHAR(20) NOT NULL
);
-- TABLE: akun
CREATE TABLE akun (
    id_akun SERIAL PRIMARY KEY,
    id_role INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    passwords VARCHAR(50) NOT NULL
);
ALTER TABLE akun
    ADD CONSTRAINT akun_role_fk FOREIGN KEY (id_role)
    REFERENCES roles(id_role);
 
-- TABLE: admins
CREATE TABLE admins (
    id_admin SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    id_akun INTEGER NOT NULL
);
ALTER TABLE admins
    ADD CONSTRAINT admins_akun_fk FOREIGN KEY (id_akun)
    REFERENCES akun(id_akun);
-- TABLE: kecamatan
CREATE TABLE kecamatan (
    id_kecamatan SERIAL PRIMARY KEY,
    nama_kecamatan VARCHAR(50) NOT NULL
);
-- TABLE: kelurahan
CREATE TABLE kelurahan (
    id_kelurahan SERIAL PRIMARY KEY,
    nama_kelurahan VARCHAR(50) NOT NULL,
    id_kecamatan INTEGER NOT NULL
);
ALTER TABLE kelurahan
    ADD CONSTRAINT kelurahan_kecamatan_fk FOREIGN KEY (id_kecamatan)
    REFERENCES kecamatan(id_kecamatan);
-- TABLE: jenis_kopi
CREATE TABLE jenis_kopi (
    id_jenis_kopi SERIAL PRIMARY KEY,
    jenis_kopi VARCHAR(100)
);
 
-- TABLE: kopi
CREATE TABLE kopi (
    id_kopi SERIAL PRIMARY KEY,
    deskripsi TEXT NOT NULL,
    harga INTEGER NOT NULL,
    jumlah_stok INTEGER NOT NULL,
    kualitas VARCHAR(1) NOT NULL,
    id_jenis_kopi INTEGER NOT NULL
);
ALTER TABLE kopi
    ADD CONSTRAINT kopi_jenis_fk FOREIGN KEY (id_jenis_kopi)
    REFERENCES jenis_kopi(id_jenis_kopi);
-- TABLE: pembeli
CREATE TABLE pembeli (
    id_pembeli SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    alamat VARCHAR(50) NOT NULL,
    id_akun INTEGER NOT NULL,
    id_kelurahan INTEGER NOT NULL
);
ALTER TABLE pembeli
    ADD CONSTRAINT pembeli_akun_fk FOREIGN KEY (id_akun)
    REFERENCES akun(id_akun);
ALTER TABLE pembeli
    ADD CONSTRAINT pembeli_kelurahan_fk FOREIGN KEY (id_kelurahan)
    REFERENCES kelurahan(id_kelurahan);
 
-- TABLE: petani_kopi
CREATE TABLE petani_kopi (
    id_petani SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    alamat VARCHAR(50) NOT NULL,
    id_akun INTEGER NOT NULL,
    id_kelurahan INTEGER NOT NULL
);
ALTER TABLE petani_kopi
    ADD CONSTRAINT petani_akun_fk FOREIGN KEY (id_akun)
    REFERENCES akun(id_akun);
ALTER TABLE petani_kopi
    ADD CONSTRAINT petani_kelurahan_fk FOREIGN KEY (id_kelurahan)
    REFERENCES kelurahan(id_kelurahan);
-- TABLE: data_penanaman
CREATE TABLE data_penanaman (
    id_penanaman SERIAL PRIMARY KEY,
    tanggal_penanaman DATE NOT NULL,
    deskripsi TEXT NOT NULL,
    jenis_kopi VARCHAR(100) NOT NULL,
    kuantitas INTEGER NOT NULL
);
-- TABLE: data_harian
CREATE TABLE data_harian (
    id_harian SERIAL PRIMARY KEY,
    id_penanaman INTEGER NOT NULL,
    tanggal_penanaman DATE NOT NULL,
    deskripsi TEXT NOT NULL
);
ALTER TABLE data_harian
    ADD CONSTRAINT dataharian_penanaman_fk FOREIGN KEY (id_penanaman)
    REFERENCES data_penanaman(id_penanaman);
-- TABLE: orders
CREATE TABLE orders (
    id_order SERIAL PRIMARY KEY,
    tanggal_order DATE NOT NULL,
    id_transaksi INTEGER,
    id_pembeli INTEGER NOT NULL
);
ALTER TABLE orders
    ADD CONSTRAINT orders_pembeli_fk FOREIGN KEY (id_pembeli)
    REFERENCES pembeli(id_pembeli);
-- TABLE: transaksi
CREATE TABLE transaksi (
    id_transaksi SERIAL PRIMARY KEY,
    tanggal_transaksi DATE NOT NULL,
    status_pembayaran VARCHAR(20) NOT NULL,
    id_order INTEGER
);
ALTER TABLE transaksi
    ADD CONSTRAINT transaksi_orders_fk FOREIGN KEY (id_order)
    REFERENCES orders(id_order);
ALTER TABLE orders
    ADD CONSTRAINT orders_transaksi_fk FOREIGN KEY (id_transaksi)
    REFERENCES transaksi(id_transaksi);
-- TABLE: detail_order
CREATE TABLE detail_order (
    id_detail_order SERIAL PRIMARY KEY,
    harga INTEGER NOT NULL,
    kuantitas INTEGER NOT NULL,
    id_order INTEGER NOT NULL,
    id_kopi INTEGER NOT NULL
);
ALTER TABLE detail_order
    ADD CONSTRAINT detailorder_kopi_fk FOREIGN KEY (id_kopi)
    REFERENCES kopi(id_kopi);
ALTER TABLE detail_order
    ADD CONSTRAINT detailorder_orders_fk FOREIGN KEY (id_order)
    REFERENCES orders(id_order);
-- TABLE: detail_petani
CREATE TABLE detail_petani (
    id_detail_petani SERIAL PRIMARY KEY,
    id_petani INTEGER NOT NULL,
    id_penanaman INTEGER NOT NULL,
    id_kopi INTEGER
);
ALTER TABLE detail_petani
    ADD CONSTRAINT detailpetani_petani_fk FOREIGN KEY (id_petani)
    REFERENCES petani_kopi(id_petani);
ALTER TABLE detail_petani
    ADD CONSTRAINT detailpetani_penanaman_fk FOREIGN KEY (id_penanaman)
    REFERENCES data_penanaman(id_penanaman);
ALTER TABLE detail_petani
    ADD CONSTRAINT detailpetani_kopi_fk FOREIGN KEY (id_kopi)
    REFERENCES kopi(id_kopi);
-- TABLE: verifikasi
CREATE TABLE verifikasi (
    id_verifikasi SERIAL PRIMARY KEY,
    id_admin INTEGER,
    id_petani INTEGER NOT NULL,
    status_verifikasi VARCHAR(10) NOT NULL,
    tanggal_terverifikasi DATE
);
ALTER TABLE verifikasi
    ADD CONSTRAINT verifikasi_admin_fk FOREIGN KEY (id_admin)
    REFERENCES admins(id_admin);
ALTER TABLE verifikasi
    ADD CONSTRAINT verifikasi_petani_fk FOREIGN KEY (id_petani)
    REFERENCES petani_kopi(id_petani);
-- TABLE: detail_verifikasi
CREATE TABLE detail_verifikasi (
    id_detail_verifikasi SERIAL PRIMARY KEY,
    kuantitas INTEGER NOT NULL,
    id_verifikasi INTEGER NOT NULL,
    id_kopi INTEGER,
    jenis_kopi_baru VARCHAR(100),
    deskripsi_baru TEXT,
    harga_baru INTEGER,
    kualitas_baru VARCHAR(1)
);
ALTER TABLE detail_verifikasi
    ADD CONSTRAINT detailverifikasi_verifikasi_fk FOREIGN KEY (id_verifikasi)
    REFERENCES verifikasi(id_verifikasi);
ALTER TABLE detail_verifikasi
    ADD CONSTRAINT detailverifikasi_kopi_fk FOREIGN KEY (id_kopi)
    REFERENCES kopi(id_kopi);
-- TABLE: feedback
CREATE TABLE feedback (
    id_feedback SERIAL PRIMARY KEY,
    id_admin INTEGER NOT NULL,
    id_harian INTEGER NOT NULL,
    tanggal_feedback DATE NOT NULL,
    status_verifikasi VARCHAR(20) ,
    catatan_feedback TEXT NOT NULL
);
ALTER TABLE feedback
    ADD CONSTRAINT feedback_admin_fk FOREIGN KEY (id_admin)
    REFERENCES admins(id_admin);
ALTER TABLE feedback
    ADD CONSTRAINT feedback_harian_fk FOREIGN KEY (id_harian)
    REFERENCES data_harian(id_harian);

INSERT INTO roles (nama_role)
VALUES ('admin'),
('petani'),
('pembeli')

INSERT INTO akun (id_role, username, passwords)
VALUES (1, 'admin', '123')
RETURNING id_akun;

INSERT INTO admins (nama, no_telp, id_akun)
VALUES ('Budi', '08123456789',1);
