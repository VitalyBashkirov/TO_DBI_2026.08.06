# -*- coding: utf-8 -*-
from pathlib import Path
import sys, json, shutil

J  = Path(r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json")
BK = Path(r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json.ds70_12bak")

OLD_VAL = r"in\s+::\[\w+\]\s*(?!all|collection)"
NEW_VAL = r"in\s+(?:::\[\w+\]|this(?:\(\w+\))?\.\[\w+\])\s*(?!all|collection)"

raw = J.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
data = json.loads(text)

rule = data["rules"]["plpcheck.EXIST_ALL_OR_COLLECTIONS"]
cur_val = rule["regex_patterns"]["for_search"][0]["pattern"]
print("[patch] current for_search[0].pattern repr = " + repr(cur_val))
print("[patch] OLD_VAL                      repr = " + repr(OLD_VAL))
if cur_val != OLD_VAL:
    print("[patch] ABORT: текущее значение не совпадает с ожидаемым OLD_VAL")
    sys.exit(2)

# JSON-escaped строка старого значения: то, что реально в файле внутри кавычек.
old_esc = json.dumps(OLD_VAL)[1:-1]
new_esc = json.dumps(NEW_VAL)[1:-1]
print("[patch] old_esc = " + old_esc)
print("[patch] new_esc = " + new_esc)

old_count = text.count(old_esc)
print("[patch] old_esc occurrences in file = " + str(old_count))
if old_count != 1:
    print("[patch] ABORT: ожидалось ровно 1 вхождение OLD в файле")
    sys.exit(3)

new_text = text.replace(old_esc, new_esc, 1)
if new_text.count(old_esc) != 0:
    print("[patch] ABORT: после замены old_esc всё ещё присутствует")
    sys.exit(4)
if new_text.count(new_esc) != 1:
    print("[patch] ABORT: после замены new_esc не ровно 1 раз")
    sys.exit(5)

# Проверка парсинга и точного попадания в нужное поле
data2 = json.loads(new_text)
val2 = data2["rules"]["plpcheck.EXIST_ALL_OR_COLLECTIONS"]["regex_patterns"]["for_search"][0]["pattern"]
print("[patch] after for_search[0].pattern repr = " + repr(val2))
if val2 != NEW_VAL:
    print("[patch] ABORT: значение после правки не NEW_VAL")
    sys.exit(6)

if not BK.exists():
    BK.write_bytes(raw)
    print("[patch] backup: " + BK.name + " (" + str(len(raw)) + " bytes)")
else:
    print("[patch] backup exists: " + BK.name)

new_bytes = new_text.encode("utf-8")
if has_bom:
    new_bytes = b"\xef\xbb\xbf" + new_bytes
J.write_bytes(new_bytes)
print("[patch] wrote " + J.name + " (" + str(len(new_bytes)) + " bytes, bom=" + str(has_bom) + ")")
