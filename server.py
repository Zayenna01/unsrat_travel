
from pathlib import Path
import sys

from flask import (
    render_template_string,
    request,
    send_from_directory
)

# ==========================================
# LOKASI FOLDER
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

PROJECT_DIR = (
    BASE_DIR / "unsrat_apriori_web" / "unsrat_apriori_web"
)

HTML_FILE = BASE_DIR / "index.html"

if not (PROJECT_DIR / "app.py").is_file():
    raise FileNotFoundError(
        f"app.py tidak ditemukan: {PROJECT_DIR / 'app.py'}"
    )

if not HTML_FILE.is_file():
    raise FileNotFoundError(
        f"index.html tidak ditemukan: {HTML_FILE}"
    )

# ==========================================
# IMPORT APLIKASI ASLI
# ==========================================

sys.path.insert(0, str(PROJECT_DIR))

import app as original

flask_app = original.app

# ==========================================
# ROUTE CSS
# ==========================================

@flask_app.route("/assets/<path:filename>")
def external_assets(filename):
    return send_from_directory(
        PROJECT_DIR / "static",
        filename
    )

# ==========================================
# HALAMAN INDEX EKSTERNAL
# ==========================================

def external_index():

    print("\n[DIAGNOSTIK] external_index BERHASIL DIPANGGIL")

    min_support = 0.30
    min_confidence = 0.80

    analyzed = False
    levels = []
    rules = []
    min_count = 0
    error = None

    if request.method == "POST":
        try:
            min_support = (
                float(request.form.get("min_support", "30")) / 100
            )

            min_confidence = (
                float(request.form.get("min_confidence", "80")) / 100
            )

            if not (
                0 < min_support <= 1
                and 0 < min_confidence <= 1
            ):
                raise ValueError(
                    "Support dan confidence harus lebih dari 0 "
                    "dan maksimal 100%."
                )

            levels, rules, min_count = original.apriori(
                original.TRANSACTIONS,
                min_support,
                min_confidence
            )

            analyzed = True

        except ValueError as exc:
            error = str(exc)

    unique_cities = sorted({
        city
        for items in original.TRANSACTIONS.values()
        for city in items
    })

    frequent_count = sum(
        len(level["frequent"])
        for level in levels
    )

    template = HTML_FILE.read_text(encoding="utf-8")

    return render_template_string(
        template,
        transactions=original.TRANSACTIONS,
        city_count=len(unique_cities),
        unique_cities=unique_cities,
        min_support=min_support,
        min_confidence=min_confidence,
        analyzed=analyzed,
        levels=levels,
        rules=rules,
        min_count=min_count,
        frequent_count=frequent_count,
        error=error
    )

# ==========================================
# GANTI FUNGSI INDEX ASLI
# ==========================================

root_rules = [
    rule for rule in flask_app.url_map.iter_rules()
    if rule.rule == "/"
]

print("\n[DIAGNOSTIK] ROUTE HALAMAN UTAMA:")

for rule in root_rules:
    print("Endpoint:", rule.endpoint)
    print("Methods :", rule.methods)

    flask_app.view_functions[rule.endpoint] = external_index

print("[DIAGNOSTIK] Fungsi index telah diganti.")

# ==========================================
# CATAT SETIAP PERMINTAAN BROWSER
# ==========================================

@flask_app.before_request
def diagnostic_request():
    print(
        f"\n[REQUEST MASUK] {request.method} {request.path}"
    )

# ==========================================
# JALANKAN SERVER PADA PORT 5001
# ==========================================

if __name__ == "__main__":

    print("\n======================================")
    print(" SISTEM APRIORI UNSRAT - TES SERVER")
    print("======================================")
    print("Index HTML :", HTML_FILE)
    print("App Python :", PROJECT_DIR / "app.py")
    print("Port       : 5001")
    print("======================================")

    flask_app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
        use_reloader=False
    )
