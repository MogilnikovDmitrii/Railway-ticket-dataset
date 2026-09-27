import random

from src.config.config import (
    payment_system_coefficients,
    bank_coefficients,
    payment_systems_bins
)



def generate_card(payment_system_coefficients, bank_coefficients):
    payment_system = random.choices(list(payment_system_coefficients.keys()),weights=list(payment_system_coefficients.values()),k=1)[0]

    bank = random.choices(list(bank_coefficients.keys()),weights=list(bank_coefficients.values()),k=1)[0]

    bins = payment_systems_bins[payment_system][bank]

    bin_code = random.choice(bins)

    remaining_digits = ''.join(
        random.choices("0123456789", k=9)
    )

    card_number = bin_code + remaining_digits
    last_char = luhn(card_number)

    return card_number + last_char

def luhn(number):
    total = 0

    for i, digit in enumerate(number):
        digit = int(digit)

        if i % 2 == 0:
            digit *= 2

            if digit > 9:
                digit -= 9

        total += digit

    return str((10 - total % 10) % 10)

