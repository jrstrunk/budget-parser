import parsers
from hooks import hooks

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

sorted_transactions = parsers.sort_transactions(all_transactions)

altered_transactions = []
for tran in sorted_transactions:
    hooked = False
    for hook in hooks:
        for altered_tran in hook(tran):
            hooked = True
            altered_transactions.append(altered_tran)
    if not hooked:
        altered_transactions.append(tran)

month = input(
    "Please enter the numerical value for " 
    + "the month which would you like transactions for:"
)

with open("transaction_output.txt", "w") as f:
    for tran in [t for t in altered_transactions 
            if int(month) == int(t.get_month())]:
        print(tran.get_formatted_transaction(), end="", file=f)

print(
    "Finishing parsing transactions!",
    "They are listed in transaction_output.txt"
)