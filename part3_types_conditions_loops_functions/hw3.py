#!/usr/bin/env python
from typing import Any, Dict, List, Optional, Tuple

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NOT_EXISTS_CATEGORY = "Category not exists!"

EXPENSE_CATEGORIES = {
    "Food": ["Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"],
    "Transport": ["Taxi", "Public transport", "Gas", "Car service"],
    "Housing": ["Rent", "Utilities", "Repairs", "Furniture"],
    "Health": ["Pharmacy", "Doctors", "Dentist", "Lab tests"],
    "Entertainment": ["Movies", "Concerts", "Games", "Subscriptions"],
    "Clothing": ["Outerwear", "Casual", "Shoes", "Accessories"],
    "Education": ["Courses", "Books", "Tutors"],
    "Communications": ["Mobile", "Internet", "Subscriptions"],
    "Other": ["SomeCategory", "SomeOtherCategory"],
}

financial_transactions_storage: List[Any] = []


def cost_categories_handler() -> str:
    lines: List[str] = []
    for main_cat, subcats in EXPENSE_CATEGORIES.items():
        lines.extend(f"{main_cat}::{sub}" for sub in subcats)
    return "\n".join(lines)


def validate_category(category: str) -> bool:
    if "::" not in category:
        return False
    main_cat, sub_cat = category.split("::", 1)
    return main_cat in EXPENSE_CATEGORIES and sub_cat in EXPENSE_CATEGORIES[main_cat]


def is_leap_year(year: int) -> bool:
    if year % 4 != 0:
        return False
    if year % 100 == 0 and year % 400 != 0:
        return False
    return True


def max_days(month: int, year: int) -> int:
    if month == 2:
        return 29 if is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def to_int(s: str) -> Optional[int]:
    if not s:
        return None
    result = 0
    for ch in s:
        if ch < '0' or ch > '9':
            return None
        result = result * 10 + (ord(ch) - ord('0'))
    return result


def parse_date(date_str: str) -> Optional[Tuple[int, int, int]]:
    parts = date_str.split("-")
    if len(parts) != 3:
        return None

    day = to_int(parts[0])
    month = to_int(parts[1])
    year = to_int(parts[2])

    if day is None or month is None or year is None:
        return None

    if month < 1 or month > 12:
        return None

    if day < 1 or day > max_days(month, year):
        return None

    return (day, month, year)


def add_error_marker() -> None:
    financial_transactions_storage.append(None)


def income_handler(amount: float, date_str: str) -> str:
    if amount <= 0:
        add_error_marker()
        return NONPOSITIVE_VALUE_MSG

    date_tuple = parse_date(date_str)
    if date_tuple is None:
        add_error_marker()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": date_tuple,
    })
    return OP_SUCCESS_MSG


def cost_handler(category: str, amount: float, date_str: str) -> str:
    if not validate_category(category):
        add_error_marker()
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        add_error_marker()
        return NONPOSITIVE_VALUE_MSG

    date_tuple = parse_date(date_str)
    if date_tuple is None:
        add_error_marker()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "type": "cost",
        "category": category,
        "amount": amount,
        "date": date_tuple,
    })
    return OP_SUCCESS_MSG


def is_on_or_before(date1: Tuple[int, int, int], date2: Tuple[int, int, int]) -> bool:
    d1, m1, y1 = date1
    d2, m2, y2 = date2

    if y1 < y2:
        return True
    if y1 > y2:
        return False
    if m1 < m2:
        return True
    if m1 > m2:
        return False
    return d1 <= d2


def stats_handler(date_str: str) -> str:
    target = parse_date(date_str)
    if target is None:
        return INCORRECT_DATE_MSG

    total = 0.0
    monthly_income = 0.0
    monthly_expenses = 0.0
    monthly_costs: Dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if transaction is None:
            continue

        trans_date = transaction["date"]
        if not is_on_or_before(trans_date, target):
            continue

        amount = transaction["amount"]

        if transaction["type"] == "income":
            total += amount
            if trans_date[1] == target[1] and trans_date[2] == target[2]:
                monthly_income += amount
        else:
            total -= amount
            if trans_date[1] == target[1] and trans_date[2] == target[2]:
                monthly_expenses += amount
                category = transaction["category"]
                monthly_costs[category] = monthly_costs.get(category, 0.0) + amount

    total = round(total, 2)
    monthly_income = round(monthly_income, 2)
    monthly_expenses = round(monthly_expenses, 2)
    amount_word = "loss" if total < 0 else "profit"

    details_lines = []
    for idx, (cat, amt) in enumerate(sorted(monthly_costs.items()), 1):
        details_lines.append(f"{idx}. {cat}: {amt:.2f}")
    category_details = "\n".join(details_lines)

    day, month, year = target
    date_fmt = f"{day:02d}-{month:02d}-{year}"

    return (
        f"Your statistics as of {date_fmt}:\n"
        f"Total capital: {total:.2f} rubles\n"
        f"This month, the {amount_word} amounted to {total:.2f} rubles.\n"
        f"Income: {monthly_expenses:.2f} rubles\n"
        f"Expenses: {monthly_income:.2f} rubles\n\n"
        f"Details (category: amount):\n"
        f"{category_details}"
    )


def parse_amount(s: str) -> Optional[float]:
    s = s.replace(",", ".")
    parts = s.split(".")

    if len(parts) > 2:
        return None

    integer_part = to_int(parts[0])
    if integer_part is None:
        return None

    fractional_part = 0
    if len(parts) == 2:
        if len(parts[1]) > 2:
            return None
        fractional_part = to_int(parts[1])
        if fractional_part is None:
            return None

    result = float(integer_part) + float(fractional_part) / 100.0
    return result


def main() -> None:
    while True:
        line = input()
        if not line:
            continue

        parts = line.split()
        if not parts:
            continue

        cmd = parts[0]
        args = parts[1:]

        if cmd == "income":
            if len(args) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = parse_amount(args[0])
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
                continue

            print(income_handler(amount, args[1]))

        elif cmd == "cost":
            if len(args) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = parse_amount(args[1])
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
                continue

            print(cost_handler(args[0], amount, args[2]))

        elif cmd == "stats":
            if len(args) != 1:
                print(UNKNOWN_COMMAND_MSG)
                continue

            print(stats_handler(args[0]))

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
