import re
from transaction_categories import categories, exclude_list
from datetime import datetime

def parse_sofi_banking_transactions(raw_trans_html: str):
    '''parses the transaction log in sofi and outputs it in a csv format. 
        the raw_trans_html string should start with "<tr data-mjs-value="'''
    formatted_transactions = []

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
            split_trans[0] = datetime\
                .strptime(split_trans[0], "%B %d %Y")\
                .strftime('%m/%d/%Y')

            formatted_transaction = split_trans[0].split('/')[2] \
                + split_trans[0].split('/')[0] + "," \
                + ",".join(split_trans)

            formatted_transactions.append(formatted_transaction)
    return formatted_transactions

def parse_sofi_credit_transactions(raw_trans_html: str):
    formatted_transactions = []

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

        trans_details = trans_details[2].split('/')[2] \
            + trans_details[2].split('/')[0] + "," \
            +f"{trans_details[2]},{trans_details[0]},{trans_details[1]}"
            
        formatted_transactions.append(trans_details)
    return formatted_transactions

def parse_discover_transactions(raw_trans_html: str):
    formatted_transactions = []

    trans_table_rows = raw_trans_html\
        .split('<tbody id="postedTransactionData">')[1]\
        .split("</tbody>")[0]\
        .split("<tr")
    del trans_table_rows[0]
    
    for trans_row in trans_table_rows:
        date = datetime.strptime(
            trans_row.split('data-date="')[1].split('"')[0], "%Y%m%d")\
            .strftime('%m/%d/%Y')
        desc = trans_row.split('class="descTxt">')[1]\
            .split("</span>")[0]\
            .replace(",", "")\
            .replace("\n", "")\
            .replace("/", " ")
        val = trans_row.split('class="amountVal ')[1]\
            .split("</td>")[0]\
            .split(">")[1]
        if "-" in val:
            val = val.replace("-", "")
        else:
            val = "-" + val
        
        formatted_transaction = date.split('/')[2] \
            + date.split('/')[0] + "," \
            + f"{date},{desc},{val}"

        formatted_transactions.append(formatted_transaction)
    return formatted_transactions

def categorize_transactions(trans: list):
    cat_trans = []
    for tran in trans:
        # check each trans for the items in the exclude list, if they are in 
        # the exclude list, continue to the next item so they are not added
        # to the final list of transactions to return
        skip = False
        for ex in exclude_list:
            if ex in tran:
                skip = True
                break
        if skip:
            continue

        # add a category for each transaction, if a transaction has no 
        # known category, it is assumed to have a category of Misc
        category = "Misc"
        sub_category = "Misc"
        for cat in categories:
            for sub_cat in categories[cat]:
                for title in categories[cat][sub_cat]:
                    if title.lower() in tran.lower():
                        category = cat
                        sub_category = sub_cat
                        break
        tran += "," + category + "," + sub_category
        cat_trans.append(tran)
    return cat_trans

def sort_transactions(trans: list):
    return sorted(
        trans, 
        key=lambda x: 
            datetime(
                int(x.split(",")[1].split("/")[2]), 
                int(x.split(",")[1].split("/")[0]), 
                int(x.split(",")[1].split("/")[1])
            ), 
        reverse=True
    )

def get_transaction_category_totals(trans: list):
    month_totals = {d: {cat: 0 for cat in categories} for d in set([f"{t.split(',')[0].split('/')[0]}/{t.split(',')[0].split('/')[2]}" for t in trans])}
    for tran in trans:
        stran = tran.split(",")
        date = stran[0].split("/")[0] + "/" + stran[0].split("/")[2]
        cat = stran[3].replace("\n", "")
        val = -1 * float(stran[2].replace("$", ""))
        month_totals[date][cat] += val
    return month_totals