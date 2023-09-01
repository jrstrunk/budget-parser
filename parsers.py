import re
from datetime import datetime
from transaction_categories import categories, exclude_list
from input.manual_transactions import manual_transactions
from transaction import Transaction

def parse_sofi_banking_transactions(raw_trans_html: str):
    '''parses the transaction log in sofi and outputs it in a csv format. 
        the raw_trans_html string should start with "<tr data-mjs-value="'''
    transactions = []

    # parse the whole page down to the needed tables
    secs = raw_trans_html.split('<div class="transactions"')
    trans_sec = secs[1]
    tbodies = trans_sec.split("tbody")
    real_tbodies = [b for b in tbodies if "<tr " in b]
    
    for tbody in real_tbodies:
        split_items = tbody.split('</tr>')
        del split_items[-1]

        for item in split_items:
            trans = re.findall('<title>.+</title>', item)
            trans = re.sub('<\/*title>', '', trans[0])
            trans = re.sub('Transaction. Date: ', '', trans)
            trans = re.sub(',', '', trans)
            trans = re.sub('. Description: ', ',', trans)
            trans = re.sub('\ *. Amount: ', ',', trans)
            trans = trans[:-1]

            # format the date
            split_trans = trans.split(",")
            date = datetime.strptime(split_trans[0], "%B %d %Y")
            # cast the amount to a float
            amount = float(split_trans[2].replace("$", ""))

            transactions.append(
                Transaction(date, split_trans[1], amount)
            )
    return transactions

def parse_sofi_credit_transactions(raw_trans_html: str):
    transactions = []

    transaction_groups = raw_trans_html.split('data-qa="posted-transaction-item"')
    del transaction_groups[0]
    transaction_groups = [t.split("</span>")[0] for t in transaction_groups]

    # remove every odd group because there are two listings for every transaction
    transaction_groups = [t for i, t in enumerate(transaction_groups) if i % 2 == 0]

    # parse the whole page down to the needed tables
    for tgroup in transaction_groups:
        trans_details = tgroup.split('<p')
        del trans_details[0]
        trans_details = [t.split(">")[1] for t in trans_details]
        trans_details = [re.sub("</p", "", t) for t in trans_details]
        trans_details = [re.sub(",", "", t) for t in trans_details]
        trans_details = [re.sub("\n", "", t) for t in trans_details]
        trans_details = [t.strip() for t in trans_details]

        # spending is positive in the credit transactions, so make all
        # negative transactions positive and all positive negative that way
        # debts will be negative and repayments/refunds will be positive
        if "-" in trans_details[1]:
            trans_details[1] = trans_details[1].replace("-", "")
        else:
            trans_details[1] = "-" + trans_details[1]

        date = datetime.strptime(trans_details[2], "%m/%d/%Y")
        amount = float(trans_details[1].replace("$", ""))
            
        transactions.append(
            Transaction(date, trans_details[0], amount)
        )
    return transactions

def parse_discover_transactions(raw_trans_html: str):
    transactions = []

    trans_table = re.findall(r"transactionTbl[^>]*>([\s\S]*?)<\/table>", raw_trans_html)[0]

    # remove the first match, the column header row
    trans_table_rows = re.findall(r"<tr[^>]*>(?:[\s\S]*?)<\/tr>", trans_table)[1:]

    for trans_row in trans_table_rows:
        date = datetime.strptime(
            re.findall(r'data-date="(.*?)"', trans_row)[0],
            "%m/%d/%Y",
        )
        name = re.findall(r'class="merchant-name">([\s\S]*?)<', trans_row)[0]\
            .replace("\n", " ")\
            .replace("&amp;", "&")
        amount = re.findall(r'data-amt="(.*?)"', trans_row)[0]

        if "-" in amount:
            amount = amount.replace("-", "")
        else:
            amount = "-" + amount
        amount = float(amount.replace("$", ""))
        
        transactions.append(
            Transaction(date, name, amount)
        )
    return transactions

def parse_venmo_transactions(raw_trans_html: str):
    return []

def parse_manual_transactions():
    return [
        Transaction(datetime.strptime(t[0], "%Y/%m/%d"), t[1], t[2]) 
            for t in manual_transactions
    ]

def sort_transactions(transactions: list):
    return sorted(
        transactions, 
        key=lambda t: t.datetime,
        reverse=True
    )
