import shutil
from datetime import datetime
import os

def backup_database():
    # SQLite veritabanı dosyasının yolunu belirtin
    database_path = os.getenv('DATABASE_PATH')
    
    # Yedekleme dosyasının adını ve yolunu oluşturun (örneğin, database_2024-06-24.db)
    backup_folder = 'backup/'
    backup_filename = f'database_{datetime.now().strftime("%Y-%m-%d")}.db'
    backup_path = os.path.join(backup_folder, backup_filename)
    
    # Yedekleme klasörünü oluşturmak ve yazma izinlerini kontrol etmek
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
        print(f"Yedekleme klasörü oluşturuldu: {backup_folder}")
    if not os.access(backup_folder, os.W_OK):
        raise OSError(f"Yedekleme klasörüne yazma izniniz yok: {backup_folder}")
    
    # Eğer yedekleme dosyası varsa yeni yedekleme dosyası oluşturmadan önce silin
    if os.path.exists(backup_path):
        os.remove(backup_path)
        
    # Veritabanı dosyasını yedekleme dosyasına kopyala
    shutil.copyfile(database_path, backup_path)
    
    print(f"Veritabanı yedeği alındı: {backup_path}")

def delete_old_backup():
    # Silinecek dosyaların sayısını belirleyin (örneğin, her üçüncü gün)
    delete_interval = 3
    backup_folder = 'backup/'
    
    # Yedeklenen dosyaları listele ve silinecek dosyaları belirle
    backup_files = os.listdir(backup_folder)
    backup_files.sort()
    files_to_delete = backup_files[:-delete_interval]
    
    # Belirlenen dosyaları sil
    for file_to_delete in files_to_delete:
        os.remove(os.path.join(backup_folder, file_to_delete))
        print(f"Silinen dosya: {file_to_delete}")

if __name__ == "__main__":
    backup_database()
    delete_old_backup()
