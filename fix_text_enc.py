
import sys, json
import pathlib, chardet

# غيّر الأنماط بحسب الحاجة
GLOBS = ["profiles/**/*.json", "templates/**/*.json", "*.json", "README.*", "*.txt", "**/*.md"]

def iter_files():
    for pat in GLOBS:
        for p in pathlib.Path(".").glob(pat):
            if p.is_file():
                yield p

converted = 0
skipped = 0
for p in iter_files():
    b = p.read_bytes()
    # لو الملف بالفعل UTF-8 صالح، نتجاوزه
    try:
        b.decode("utf-8")
        skipped += 1
        continue
    except UnicodeDecodeError:
        pass

    enc = (chardet.detect(b) or {}).get("encoding") or "utf-8"
    original_enc = enc
    try:
        text = b.decode(enc, errors="strict")
    except Exception:
        for fallback in ("cp1256", "cp1252", "latin1"):
            try:
                text = b.decode(fallback, errors="strict")
                enc = f"{original_enc}->{fallback}"
                break
            except Exception:
                continue
        else:
            text = b.decode(original_enc, errors="replace")
            enc = f"{original_enc} (replace)"
    p.write_text(text, encoding="utf-8", newline="\n")
    converted += 1
    print(f"[CONVERTED] {p}  ({enc} -> utf-8)")

print(f"Done. Converted={converted}, Skipped(utf-8)={skipped}")

