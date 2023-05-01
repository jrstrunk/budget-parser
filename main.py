import os
import parsers
from hooks import hooks

files = [
    f for f in os.listdir("./") 
        if os.path.isfile(os.path.join("./", f)) and ".html" in f
]

all_transactions = []

for input_file in files:
    trans = []
    with open(input_file) as f:
        raw_trans_html = "".join(f.readlines())
    
    if "sofi_banking" in input_file:
        trans = parsers.parse_sofi_banking_transactions(raw_trans_html)

    elif "sofi_credit" in input_file:
        trans = parsers.parse_sofi_credit_transactions(raw_trans_html)

    elif "discover_credit" in input_file:
        trans = parsers.parse_discover_transactions(raw_trans_html)

    elif "venmo" in input_file:
        trans = parsers.parse_venmo_transactions(raw_trans_html)

    all_transactions.extend(trans)

manual_trans = parsers.parse_manual_transactions()
all_transactions.extend(manual_trans)

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