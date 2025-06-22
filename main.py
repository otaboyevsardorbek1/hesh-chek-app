import hashlib
import json
import os

# ---------------- CONFIG ----------------
SCAN_DIR = "./ip_data"               # Nazorat qilinadigan papka
HASH_DB = "file_hashes.json"         # Hashlar saqlanadigan fayl
ALGO = "md5"                         # Hash algoritmi (md5 yoki sha256)

# ---------------- UTILS ----------------
def get_file_hash(filepath, algo='md5'):
    """Berilgan fayl uchun hash qaytaradi."""
    h = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan_files(directory):
    """Papkadagi barcha fayllarni skan qiladi va hashlarini qaytaradi."""
    file_hashes = {}
    for root, _, files in os.walk(directory):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                hash_val = get_file_hash(full_path, ALGO)
                rel_path = os.path.relpath(full_path, directory)
                file_hashes[rel_path] = hash_val
            except Exception as e:
                print(f"⚠️ Fayl o'qishda xatolik: {full_path} ({e})")
    return file_hashes

def load_old_hashes(filepath):
    """Oldingi hash faylini yuklaydi (agar mavjud bo‘lsa va bo‘sh bo‘lmasa)."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
                if content == "":
                    print("⚠️ Hash fayli bo‘sh. Yangi hashlar saqlanadi.")
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print("❌ Hash fayli buzilgan yoki noto‘g‘ri formatda!")
            return {}
    return {}


def save_hashes(filepath, hashes):
    """Hozirgi hash holatini faylga yozadi."""
    with open(filepath, 'w') as f:
        json.dump(hashes, f, indent=2)

def compare_hashes(old, new):
    """Eski va yangi hash’larni taqqoslab farqni aniqlaydi."""
    results = {"changed": [], "new": [], "deleted": []}
    for path in new:
        if path not in old:
            results["new"].append(path)
        elif new[path] != old[path]:
            results["changed"].append(path)
    for path in old:
        if path not in new:
            results["deleted"].append(path)
    return results

def print_diff(diff):
    """Farqni chiroyli tarzda chiqaradi."""
    print("\n📂 Fayl holatlari:")
    for key in ["new", "changed", "deleted"]:
        print(f"  ➤ {key.capitalize()}: {len(diff[key])}")
        for f in diff[key]:
            print(f"    - {f}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🔎 Skaner ishga tushdi...\n")

    new_hashes = scan_files(SCAN_DIR)
    old_hashes = load_old_hashes(HASH_DB)

    if not old_hashes:
        print("📥 Eski hashlar mavjud emas yoki bo‘sh. Yangi holat saqlanmoqda...")
        save_hashes(HASH_DB, new_hashes)
        print("✅ Hash fayli yangilandi.")
    else:
        diff = compare_hashes(old_hashes, new_hashes)
        print_diff(diff)
        save_hashes(HASH_DB, new_hashes)
        print("\n✅ Yangi hashlar saqlandi:", HASH_DB)

