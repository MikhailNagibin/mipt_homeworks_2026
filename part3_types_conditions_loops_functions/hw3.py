#!/usr/bin/env python

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

financial_transactions_storage = []


def cost_categories_handler() -> str:
    result = []
    for category, subcategories in EXPENSE_CATEGORIES.items():
        for subcategory in subcategories:
            result.append(f"{category}::{subcategory}")
    return "\n".join(result)


def validate_category(category: str) -> bool:
    if "::" not in category:
        return False
    main_cat, sub_cat = category.split("::", 1)
    return main_cat in EXPENSE_CATEGORIES and sub_cat in EXPENSE_CATEGORIES[main_cat]


def parse_date(date_str: str) -> tuple[int, int, int] | None:
    """Парсит дату из строки DD-MM-YYYY"""
    parts = date_str.split("-")
    if len(parts) != 3:
        return None

    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None

    if month < 1 or month > 12:
        return None

    days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if day < 1 or day > days_in_month[month - 1]:
        return None

    return (day, month, year)


def cost_handler(category: str, amount: float, date_str: str) -> str:
    if not validate_category(category):
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date_tuple = parse_date(date_str)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "type": "cost",
        "category": category,
        "amount": amount,
        "date": date_str
    })

    return OP_SUCCESS_MSG


def income_handler(amount: float, date_str: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date_tuple = parse_date(date_str)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": date_str
    })

    return OP_SUCCESS_MSG


class Data:
    def __init__(self):
        self._cost = {}
        self._income = {}

    def add_income(self, date: str, amount: float):
        if date not in self._income:
            self._income[date] = 0
        self._income[date] += amount

    def add_cost(self, date: str, category: str, amount: float):
        if date not in self._cost:
            self._cost[date] = {}
        if category not in self._cost[date]:
            self._cost[date][category] = 0
        self._cost[date][category] += amount

    def _is_before(self, date_parts: tuple, target_parts: tuple) -> bool:
        day, month, year = date_parts
        t_day, t_month, t_year = target_parts

        if year < t_year:
            return True
        if year > t_year:
            return False
        if month < t_month:
            return True
        if month > t_month:
            return False
        return day <= t_day

    def get_stats(self, target_date: tuple[int, int, int]):
        target_day, target_month, target_year = target_date
        target_parts = (target_day, target_month, target_year)

        total_capital = 0
        monthly_income = 0
        monthly_expenses = 0
        monthly_costs_by_category = {}

        for date_str, amount in self._income.items():
            date_parts = tuple(map(int, date_str.split("-")))
            if self._is_before(date_parts, target_parts):
                total_capital += amount
                _, month, year = date_parts
                if year == target_year and month == target_month:
                    monthly_income += amount

        for date_str, categories in self._cost.items():
            date_parts = tuple(map(int, date_str.split("-")))
            if self._is_before(date_parts, target_parts):
                day_total = sum(categories.values())
                total_capital -= day_total

                _, month, year = date_parts
                if year == target_year and month == target_month:
                    monthly_expenses += day_total
                    for category, cat_amount in categories.items():
                        monthly_costs_by_category[category] = (
                                monthly_costs_by_category.get(category, 0) + cat_amount
                        )

        return {
            "capital": total_capital,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "categories": monthly_costs_by_category,
        }


class Handler:
    def __init__(self):
        self.data = Data()
        while True:
            try:
                command_line = input().strip()
                if not command_line:
                    continue
                parts = command_line.split()
                command = parts[0]
                details = parts[1:] if len(parts) > 1 else []
                self.handler(command, details)
            except EOFError:
                break
            except KeyboardInterrupt:
                break

    def _parse_float(self, value: str) -> float | None:
        value = value.replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return None

    def handler(self, command: str, details: list):
        match command:
            case "income":
                self._income(details)
            case "cost":
                self._cost(details)
            case "stats":
                self._stats(details)
            case _:
                print(UNKNOWN_COMMAND_MSG)

    def _income(self, details: list):
        if len(details) != EXPECTED_INCOME_ARGS:
            print(UNKNOWN_COMMAND_MSG)
            return

        amount_str, date_str = details

        amount = self._parse_float(amount_str)
        if amount is None:
            print(UNKNOWN_COMMAND_MSG)
            return

        result = income_handler(amount, date_str)
        if result != OP_SUCCESS_MSG:
            print(result)
            return

        date_tuple = parse_date(date_str)
        formatted_date = f"{date_tuple[0]:02d}-{date_tuple[1]:02d}-{date_tuple[2]}"
        self.data.add_income(formatted_date, amount)
        print(OP_SUCCESS_MSG)

    def _cost(self, details: list):
        if len(details) != EXPECTED_COST_ARGS:
            print(UNKNOWN_COMMAND_MSG)
            return

        category, amount_str, date_str = details

        amount = self._parse_float(amount_str)
        if amount is None:
            print(UNKNOWN_COMMAND_MSG)
            return

        result = cost_handler(category, amount, date_str)
        if result != OP_SUCCESS_MSG:
            print(result)
            return

        date_tuple = parse_date(date_str)
        formatted_date = f"{date_tuple[0]:02d}-{date_tuple[1]:02d}-{date_tuple[2]}"
        self.data.add_cost(formatted_date, category, amount)
        print(OP_SUCCESS_MSG)

    def _stats(self, details: list):
        if len(details) != EXPECTED_STATS_ARGS:
            print(UNKNOWN_COMMAND_MSG)
            return

        date_str = details[0]
        date_tuple = parse_date(date_str)
        if date_tuple is None:
            print(INCORRECT_DATE_MSG)
            return

        stats = self.data.get_stats(date_tuple)

        day, month, year = date_tuple
        print(f"Ваша статистика по состоянию на {day:02d}-{month:02d}-{year}:")
        print(f"Суммарный капитал: {stats['capital']:.2f} рублей")

        profit = stats['monthly_income'] - stats['monthly_expenses']
        if profit >= 0:
            print(f"Месячная прибыль составила {profit:.2f} рублей")
        else:
            print(f"Месячный убыток составил {abs(profit):.2f} рублей")

        print(f"Доходы: {stats['monthly_income']:.2f} рублей")
        print(f"Расходы: {stats['monthly_expenses']:.2f} рублей")
        print()
        print("Детализация (категория: сумма):")

        if stats['categories']:
            sorted_categories = sorted(stats['categories'].items())
            for i, (category, amount) in enumerate(sorted_categories, 1):
                print(f"{i}. {category}: {amount:.2f}")
        else:
            print()


def main() -> None:
    Handler()


if __name__ == "__main__":
    main()