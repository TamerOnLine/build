
import sys
import pathlib
import chardet

ROOTS = [pathlib.Path("st_app"), pathlib.Path("st_app/pages")]

targets = []
for r in ROOTS:
    if r.exists():
        targets += list(r.rglob("*.py"))

if not targets:
    print("No .py files under st_app/")
    sys.exit(0)

converted = 0
skipped = 0

for p in targets:
    b = p.read_bytes()
    # لو UTF-8 أصلاً، نتجاوزه
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
        # محاولات بديلة شائعة
        for fb in ("cp1256", "cp1252", "latin1", "mac_roman"):
            try:
                text = b.decode(fb, errors="strict")
                enc = f"{original_enc}->{fb}"
                break
            except Exception:
                continue
        else:
            text = b.decode(original_enc, errors="replace")
            enc = f"{original_enc} (replace)"

    # اكتب UTF-8 + LF
    p.write_text(text, encoding="utf-8", newline="\n")
    converted += 1
    print(f"[CONVERTED] {p}  ({enc} -> utf-8)")

print(f"Done. Converted={converted}, Skipped(utf-8)={skipped}, Total={len(targets)}")
