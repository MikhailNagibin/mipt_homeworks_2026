#!/usr/bin/env python
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NOT_EXISTS_CATEGORY = "Category not exists!"
EXPECTED_INCOME_ARGS = 2
EXPECTED_COST_ARGS = 3
EXPECTED_STATS_ARGS = 1

DATE_PARTS_COUNT = 3
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
FEBRUARY = 2
DAYS_IN_LEAP_FEB = 29
DAYS_IN_NORMAL_FEB = 28
DAYS_IN_SHORT_MONTH = 30
DAYS_IN_LONG_MONTH = 31

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

financial_transactions_storage: list[Any] = []


def cost_categories_handler() -> str:
    result_lines: list[str] = []
    for main_cat, subcats in EXPENSE_CATEGORIES.items():
        result_lines.extend(f"{main_cat}::{sub}" for sub in subcats)
    return "\n".join(result_lines)


def validate_category(category: str) -> bool:
    if "::" not in category:
        return False
    main_cat, sub_cat = category.split("::", 1)
    return main_cat in EXPENSE_CATEGORIES and sub_cat in EXPENSE_CATEGORIES[main_cat]


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_max_days(month: int, year: int) -> int:
    if month == FEBRUARY:
        return DAYS_IN_LEAP_FEB if is_leap_year(year) else DAYS_IN_NORMAL_FEB
    if month in (4, 6, 9, 11):
        return DAYS_IN_SHORT_MONTH
    return DAYS_IN_LONG_MONTH


def parse_date(date_str: str) -> tuple[int, int, int] | None:
    parts = date_str.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None
    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None
    if month < MIN_MONTH or month > MAX_MONTH:
        return None
    if day < MIN_DAY or day > get_max_days(month, year):
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


def is_before(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    d1, m1, y1 = date1
    d2, m2, y2 = date2
    if y1 != y2:
        return y1 < y2
    if m1 != m2:
        return m1 < m2
    return d1 <= d2


def stats_handler(date_str: str) -> str:
    target = parse_date(date_str)
    if target is None:
        return INCORRECT_DATE_MSG

    total_capital = 0.0
    monthly_income = 0.0
    monthly_expenses = 0.0
    monthly_costs: dict[str, float] = {}

    for t in financial_transactions_storage:
        if t is None:
            continue
        trans_date = t["date"]
        if not is_before(trans_date, target):
            continue
        amount = t["amount"]
        if t["type"] == "income":
            total_capital += amount
            if trans_date[1] == target[1] and trans_date[2] == target[2]:
                monthly_income += amount
        else:  # cost
            total_capital -= amount
            if trans_date[1] == target[1] and trans_date[2] == target[2]:
                monthly_expenses += amount
                cat = t["category"]
                monthly_costs[cat] = monthly_costs.get(cat, 0.0) + amount

    total_capital = round(total_capital, 2)
    monthly_income = round(monthly_income, 2)
    monthly_expenses = round(monthly_expenses, 2)
    amount_word = "loss" if total_capital < 0 else "profit"

    details_lines = []
    for idx, (cat, amt) in enumerate(sorted(monthly_costs.items()), 1):
        details_lines.append(f"{idx}. {cat}: {amt:.2f}")
    category_details = "\n".join(details_lines)

    day, month, year = target
    date_fmt = f"{day:02d}-{month:02d}-{year}"
    return (
        f"Your statistics as of {date_fmt}:\n"
        f"Total capital: {total_capital:.2f} rubles\n"
        f"This month, the {amount_word} amounted to {total_capital:.2f} rubles.\n"
        f"Income: {monthly_expenses:.2f} rubles\n"
        f"Expenses: {monthly_income:.2f} rubles\n\n"
        f"Details (category: amount):\n"
        f"{category_details}"
    )


def main() -> None:
    while True:
        try:
            line = input()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0]
            args = parts[1:]

            if cmd == "income" and len(args) == EXPECTED_INCOME_ARGS:
                try:
                    amt = float(args[0].replace(",", "."))
                except ValueError:
                    print(UNKNOWN_COMMAND_MSG)
                    continue
                print(income_handler(amt, args[1]))
            elif cmd == "cost" and len(args) == EXPECTED_COST_ARGS:
                try:
                    amt = float(args[1].replace(",", "."))
                except ValueError:
                    print(UNKNOWN_COMMAND_MSG)
                    continue
                print(cost_handler(args[0], amt, args[2]))
            elif cmd == "stats" and len(args) == EXPECTED_STATS_ARGS:
                print(stats_handler(args[0]))
            else:
                print(UNKNOWN_COMMAND_MSG)
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()
