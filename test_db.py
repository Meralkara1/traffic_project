from db import get_db_connection

def main():
    conn = get_db_connection()
    if conn:
        print(" Bağlantı başarılı!")
        conn.close()
    else:
        print(" Bağlantı başarısız.")

if __name__ == "__main__":
    main()

