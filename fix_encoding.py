
import sys
import pathlib
import chardet

root = pathlib.Path("api")
targets = list(root.rglob("*.py"))

if not targets:
    print("No .py files under api/")
    sys.exit(0)

converted = 0
skipped = 0

for p in targets:
    b = p.read_bytes()
    # إذا الملف بالفعل UTF-8، نتجاوزه
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
        # محاولات بديلة شائعة للملفات العربية/الويندوز
        for fallback in ("cp1256", "cp1252", "latin1"):
            try:
                text = b.decode(fallback, errors="strict")
                enc = f"{original_enc}->{fallback}"
                break
            except Exception:
                continue
        else:
            # آخر حل: الاستبدال (لن يفشل)
            text = b.decode(original_enc, errors="replace")
            enc = f"{original_enc} (replace)"
    # اكتب كـ UTF-8 وبنهاية سطر LF
    p.write_text(text, encoding="utf-8", newline="\n")
    converted += 1
    print(f"[CONVERTED] {p}  ({enc} -> utf-8)")

print(f"Done. Converted={converted}, Skipped(utf-8)={skipped}, Total={len(targets)}")
