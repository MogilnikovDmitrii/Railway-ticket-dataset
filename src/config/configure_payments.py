import json

from src.config.config import (
    PAYMENT_SETTINGS_FILE,
    bank_coefficients,
    payment_system_coefficients,
)


def read_percentages(title: str, current: dict[str, int]) -> dict[str, int]:
    print(f"\n{title}")
    print("Текущие значения: " + ", ".join(
        f"{name}: {value}%" for name, value in current.items()
    ))

    while True:
        result = {}
        for name in current:
            while True:
                value = input(f"{name}, %: ").strip().replace(",", ".")
                try:
                    percentage = float(value)
                except ValueError:
                    print("Введите неотрицательное число.")
                    continue

                if percentage < 0:
                    print("Процент не может быть отрицательным.")
                    continue

                result[name] = percentage
                break

        if sum(result.values()) == 100:
            return result

        print(
            f"Сумма введенных процентов: {sum(result.values()):g}. "
            "Она должна быть равна 100. Повторите ввод."
        )


payment_systems = read_percentages(
    "Распределение платежных систем", payment_system_coefficients
)
banks = read_percentages("Распределение банков", bank_coefficients)

settings = {
    "payment_system_coefficients": payment_systems,
    "bank_coefficients": banks,
}
with PAYMENT_SETTINGS_FILE.open("w", encoding="utf-8") as file:
    json.dump(settings, file, ensure_ascii=False, indent=2)

print(f"\nНастройки сохранены: {PAYMENT_SETTINGS_FILE}")
