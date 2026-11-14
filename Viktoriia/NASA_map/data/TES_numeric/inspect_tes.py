
from pathlib import Path
import numpy as np

# ==========================================
# 1. НАЛАШТУВАННЯ
# ==========================================

DATA_DIR = Path(__file__).resolve().parent

ROWS = 3600
COLS = 7200

BINS = [5, 50, 100, 150, 200, 250, 300,
        400, 500, 750, 1000, 2000, 5000]


def find_file(filename):
    """Знаходить файл у папці та її підпапках."""
    matches = [
        p for p in DATA_DIR.rglob("*")
        if p.is_file() and p.name.lower() == filename.lower()
    ]

    if not matches:
        raise FileNotFoundError(
            f"Не знайдено файл: {filename}"
        )

    return matches[0]


# ==========================================
# 2. ЗЧИТУВАННЯ ДАНИХ
# ==========================================

def load_map(filename):
    path = find_file(filename)

    data = np.fromfile(path, dtype=">i2")

    if data.size != ROWS * COLS:
        raise ValueError(
            f"Неправильний розмір карти {filename}: "
            f"{data.size} значень"
        )

    return data.reshape((ROWS, COLS))


def load_mask(filename):
    path = find_file(filename)

    data = np.fromfile(path, dtype=np.uint8)

    if data.size != ROWS * COLS:
        raise ValueError(
            f"Неправильний розмір маски {filename}: "
            f"{data.size} значень"
        )

    return data.reshape((ROWS, COLS))


# ==========================================
# 3. СТАТИСТИКА ОДНІЄЇ КАРТИ
# ==========================================

def analyze_map(name, data, mask):

    print("\n" + "=" * 65)
    print(f"АНАЛІЗ: {name}")
    print("=" * 65)

    valid = data[mask != 0]

    print("\nРОЗМІР:")
    print("Карта:", data.shape)
    print("Маска:", mask.shape)

    print("\nМАСКА:")

    values, counts = np.unique(
        mask, return_counts=True
    )

    for value, count in zip(values, counts):
        print(
            f"Значення {value}: "
            f"{count:,} пікселів "
            f"({count / mask.size * 100:.2f}%)"
        )

    print("\nОСНОВНА СТАТИСТИКА:")
    print("Кількість валідних пікселів:", len(valid))
    print("Мінімум:", valid.min())
    print("Максимум:", valid.max())
    print("Середнє:", round(float(valid.mean()), 2))
    print("Медіана:", float(np.median(valid)))

    print("\nПЕРЦЕНТИЛІ:")

    for p in [5, 25, 50, 75, 90, 95, 97, 98, 99, 99.5, 99.9]:
        print(
            f"{p}%: "
            f"{np.percentile(valid, p):.2f}"
        )

    print("\nРОЗПОДІЛ ЗНАЧЕНЬ:")

    counts, edges = np.histogram(
        valid, bins=BINS
    )

    for i in range(len(counts)):
        percentage = counts[i] / len(valid) * 100

        print(
            f"{edges[i]:.0f}–{edges[i+1]:.0f}: "
            f"{counts[i]:,} пікселів "
            f"({percentage:.2f}%)"
        )

    print("\nВИСОКІ ЗНАЧЕННЯ (>1000):")

    high = valid[valid > 1000]

    print("Кількість:", len(high))

    if len(high) > 0:
        print("Мінімум:", high.min())
        print("Максимум:", high.max())
        print("Середнє:", round(float(high.mean()), 2))

        unique, freq = np.unique(
            high, return_counts=True
        )

        order = np.argsort(freq)[::-1]

        print("15 найчастіших значень:")

        for i in order[:15]:
            print(
                f"{unique[i]}: {freq[i]:,} пікселів"
            )

    return valid


# ==========================================
# 4. ЗАВАНТАЖЕННЯ НІЧНОЇ ТА ДЕННОЇ КАРТ
# ==========================================

print("=" * 65)
print("NASA MGS TES — АНАЛІЗ ТЕПЛОВОЇ ІНЕРЦІЇ МАРСА")
print("=" * 65)

print("\nЗавантажуємо нічну карту...")
night = load_map("global_ti_night_2007.img")

print("Завантажуємо нічну маску...")
night_mask = load_mask("global_ti_msk_night_2007.img")

print("Завантажуємо денну карту...")
day = load_map("global_ti_day_2007.img")

print("Завантажуємо денну маску...")
day_mask = load_mask("global_ti_msk_day_2007.img")

print("\nУсі чотири файли успішно зчитано!")


# ==========================================
# 5. АНАЛІЗ НІЧНОЇ КАРТИ
# ==========================================

night_valid = analyze_map(
    "НІЧНА ТЕПЛОВА ІНЕРЦІЯ",
    night,
    night_mask
)


# ==========================================
# 6. АНАЛІЗ ДЕННОЇ КАРТИ
# ==========================================

day_valid = analyze_map(
    "ДЕННА ТЕПЛОВА ІНЕРЦІЯ",
    day,
    day_mask
)


# ==========================================
# 7. ПОРІВНЯННЯ ДЕННОЇ ТА НІЧНОЇ КАРТ
# ==========================================

print("\n" + "=" * 65)
print("ПОРІВНЯННЯ ДЕННОЇ ТА НІЧНОЇ КАРТ")
print("=" * 65)

# Беремо тільки пікселі, які не інтерпольовані
# в обох картах одночасно.

common_mask = (
    (night_mask != 0) &
    (day_mask != 0)
)

common_count = int(np.count_nonzero(common_mask))

print("\nСпільних валідних пікселів:", f"{common_count:,}")
print(
    "Частка від усієї карти:",
    f"{common_count / common_mask.size * 100:.2f}%"
)

# Порівняння на спільних пікселях
night_common = night[common_mask]
day_common = day[common_mask]

difference = (
    day_common.astype(np.int32) -
    night_common.astype(np.int32)
)

print("\nНІЧНІ ЗНАЧЕННЯ НА СПІЛЬНИХ ПІКСЕЛЯХ:")
print("Середнє:", round(float(night_common.mean()), 2))
print("Медіана:", float(np.median(night_common)))

print("\nДЕННІ ЗНАЧЕННЯ НА СПІЛЬНИХ ПІКСЕЛЯХ:")
print("Середнє:", round(float(day_common.mean()), 2))
print("Медіана:", float(np.median(day_common)))

print("\nРІЗНИЦЯ (ДЕНЬ - НІЧ):")
print("Мінімум:", int(difference.min()))
print("Максимум:", int(difference.max()))
print("Середнє:", round(float(difference.mean()), 2))
print("Медіана:", float(np.median(difference)))

print("\nПЕРЦЕНТИЛІ РІЗНИЦІ:")

for p in [5, 25, 50, 75, 95]:
    print(
        f"{p}%: "
        f"{np.percentile(difference, p):.2f}"
    )

# Кореляція на рівномірній вибірці пікселів
# Щоб не витрачати зайву пам'ять.

flat_indices = np.flatnonzero(
    common_mask.ravel()
)[::100]

night_sample = night.ravel()[flat_indices].astype(float)
day_sample = day.ravel()[flat_indices].astype(float)

correlation = np.corrcoef(
    night_sample, day_sample
)[0, 1]

print("\nКОРЕЛЯЦІЯ ДЕННИХ І НІЧНИХ ДАНИХ:")
print("Коефіцієнт Пірсона:", round(float(correlation), 4))
print("Кількість точок у вибірці:", len(flat_indices))


# ==========================================
# 8. ЗАВЕРШЕННЯ
# ==========================================

print("\n" + "=" * 65)
print("АНАЛІЗ ЗАВЕРШЕНО УСПІШНО!")
print("=" * 65)


# ==========================================
# 9. ДОДАТКОВА ПЕРЕВІРКА МАСОК І ДІАПАЗОНІВ
# ==========================================

print("\n" + "=" * 65)
print("ДОДАТКОВА ПЕРЕВІРКА")
print("=" * 65)

# 20 пікселів на градус.
# Від 90°N до 87°N — 60 рядків.
# Від 87°S до 90°S — останні 60 рядків.

inside = slice(60, 3540)

for name, mask in [
    ("Нічна маска", night_mask),
    ("Денна маска", day_mask)
]:
    print(f"\n{name}:")

    for region_name, region in [
        ("Уся карта", mask),
        ("Між 87°N та 87°S", mask[inside]),
        ("Полярні області поза 87°", np.concatenate([
            mask[:60].ravel(),
            mask[3540:].ravel()
        ]))
    ]:
        zeros = np.count_nonzero(region == 0)
        total = region.size

        print(
            f"{region_name}: "
            f"нульових = {zeros:,} "
            f"({zeros / total * 100:.2f}%)"
        )

# Перевірка крайніх значень карт
for name, data, mask in [
    ("Нічна", night, night_mask),
    ("Денна", day, day_mask)
]:
    valid = data[mask != 0]

    print(f"\n{name} карта — крайні значення:")

    for value in [0, 1, 5, 4999, 5000, 32767, -32768]:
        print(
            f"{value}: "
            f"{np.count_nonzero(valid == value):,} пікселів"
        )

# Перевірка опису денної маски
print("\nОПИС ДЕННОЇ МАСКИ:")

day_mask_label = find_file("global_ti_msk_day_2007.lbl")

label_text = day_mask_label.read_text(
    encoding="latin-1"
)

for line in label_text.splitlines():
    if any(
        key in line.upper()
        for key in [
            "SAMPLE_TYPE",
            "SAMPLE_BITS",
            "DESCRIPTION",
            "0 <",
            "1 <",
            "MISSING_CONSTANT",
            "VALID_MINIMUM",
            "VALID_MAXIMUM"
        ]
    ):
        print(line.strip())

print("\nДОДАТКОВУ ПЕРЕВІРКУ ЗАВЕРШЕНО")
