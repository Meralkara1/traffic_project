import psycopg2

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="trafik_db",
            user="postgres",  # ya da sen hangi kullanıcıyla giriş yaptıysan
            password="postgres123",  # postgres için belirlediğin şifre
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print("Veritabanına bağlanırken hata oluştu:", e)
        return None

def veri_ekle(acil_no, ilce, mahalle, ihbar_metin, tahmin, tarih):
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ihbarlar (acil_no, ilce, mahalle, ihbar_metin, tahmin, tarih)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (acil_no, ilce, mahalle, ihbar_metin, tahmin, tarih))
        conn.commit()
        cur.close()
    except Exception as e:
        print("Veri eklenirken hata:", e)
    finally:
        conn.close()

def veri_listele():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT acil_no, ilce, mahalle, ihbar_metin, tahmin, tarih
            FROM ihbarlar
            ORDER BY tarih DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        print("Veri alınırken hata:", e)
        return []
    finally:
        conn.close()
