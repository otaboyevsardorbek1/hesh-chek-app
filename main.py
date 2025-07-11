import hashlib
import json
import os
import sys

def get_file_hash(filepath, algo='md5'):
    h = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan_files(directory, algo='md5'):
    results = []
    for root, dirs, files in os.walk(directory):
        rel_dir = os.path.relpath(root, directory)
        if rel_dir == ".":
            rel_dir = "/"
        else:
            rel_dir = "/" + rel_dir.replace("\\", "/")
        file_data = []
        for idx, filename in enumerate(files, 1):
            full_path = os.path.join(root, filename)
            try:
                hash_val = get_file_hash(full_path, algo)
                file_data.append({
                    "id": idx,
                    "file_name": filename,
                    "file_hesh_data": hash_val
                })
            except Exception as e:
                print(f"⚠️ Fayl o'qishda xatolik: {full_path} ({e})")
        if file_data:
            results.append({
                "file_path": rel_dir,
                "file_data": file_data
            })
    return results

def save_results(base_dir, data):
    save_dir = os.path.join(base_dir, 'hech_chek')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'hech_data.json')
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Natijalar saqlandi: {save_path}")

def parse_path_arg():
    """Komanda qatoridan path ni -path= yoki oddiy argument sifatida oladi."""
    for arg in sys.argv[1:]:
        if arg.startswith('-path='):
            return arg.split('=', 1)[1]
        elif not arg.startswith('-'):
            return arg
    return None

if __name__ == "__main__":
    scan_dir = parse_path_arg()
    # Agar argument/topilmadi, foydalanuvchidan so‘rash
    if not scan_dir:
        scan_dir = input("Teskiriladigan papka pathini kiriting: ").strip()
    if not os.path.isdir(scan_dir):
        print("❌ Berilgan path mavjud emas yoki papka emas!")
        sys.exit(1)
    print("🔎 Skaner ishlamoqda...")
    results = scan_files(scan_dir, algo='md5')
    save_results(scan_dir, results)
