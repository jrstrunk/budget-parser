import parsers

all_transactions = []

with open("sofi_banking.html") as f:
    raw_banking_trans_html = "".join(f.readlines())
banking_trans = parsers.parse_sofi_banking_transactions(raw_banking_trans_html)
all_transactions.extend(banking_trans)

with open("sofi_credit1.html") as f:
    raw_credit1_trans_html = "".join(f.readlines())
credit1_trans = parsers.parse_sofi_credit_transactions(raw_credit1_trans_html)
all_transactions.extend(credit1_trans)

with open("sofi_credit2.html") as f:
    raw_credit2_trans_html = "".join(f.readlines())
credit2_trans = parsers.parse_sofi_credit_transactions(raw_credit2_trans_html)
all_transactions.extend(credit2_trans)

with open("discover_credit.html") as f:
    raw_dcredit_trans_html = "".join(f.readlines())
dcredit_trans = parsers.parse_discover_transactions(raw_dcredit_trans_html)
all_transactions.extend(dcredit_trans)

categorized_transactions = parsers.categorize_transactions(all_transactions)

sorted_transactions = parsers.sort_transactions(categorized_transactions)

with open("transaction_output.txt", "w") as f:
    for trans in sorted_transactions:
        print(trans, file=f)

_ = input("Fix any output transaction category and enter any key to continue")

with open("transaction_output.txt") as f:
    sorted_transactions = f.readlines()

cat_totals = parsers.get_transaction_category_totals(sorted_transactions)

with open("cat_totals_output.txt", "w") as f:
    for month in cat_totals:
        print(month, file=f)
        print(*[f"{c}: {t}," for c, t in cat_totals[month].items()], file=f)
