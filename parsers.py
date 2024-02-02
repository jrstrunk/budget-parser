import re
from datetime import datetime, timedelta
from transaction_categories import categories, exclude_list
from input.manual_transactions import manual_transactions
from transaction import Transaction
from bs4 import BeautifulSoup

def parse_sofi_banking_transactions(raw_trans_html: str):
    '''parses the transaction log in sofi and outputs it in a csv format. 
        the raw_trans_html string should start with "<tr data-mjs-value="'''
    transactions = []

    if not raw_trans_html:
        return transactions

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

            name = split_trans[1]

            if "," in name:
                name = "\"" + name + "\""

            transactions.append(
                Transaction(date, name, amount)
            )
    return transactions

def parse_sofi_credit_transactions(raw_trans_html: str):
    transactions = []

    if not raw_trans_html:
        return transactions

    posted_trans = raw_trans_html.split('data-qa="posted-transaction-item"')
    posted_trans = [t.split("</span>")[0] for t in posted_trans]

    # remove every even group because there are two listings for every transaction
    posted_trans = [t for i, t in enumerate(posted_trans) if i % 2 == 1]

    pending_trans = raw_trans_html.split('data-qa="pending-transaction-item"')
    pending_trans = [t.split("</span>")[0] for t in pending_trans]

    # remove every even group because there are two listings for every transaction
    pending_trans = [t for i, t in enumerate(pending_trans) if i % 2 == 1]

    transaction_groups = posted_trans + pending_trans

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

        name = trans_details[0]

        if "," in name:
            name = "\"" + name + "\""

        transactions.append(
            Transaction(date, name, amount)
        )
    return transactions

def parse_discover_transactions(raw_trans_html: str):
    transactions = []

    if not raw_trans_html:
        return transactions

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

        if "," in name:
            name = "\"" + name + "\""

        transactions.append(
            Transaction(date, name, amount)
        )
    return transactions

def parse_venmo_transactions(raw_trans_html: str):
    transactions = []

    if not raw_trans_html:
        return transactions

    trans = re.findall(r"<article[^>]*>(?:[\s\S]*?)<\/article>", raw_trans_html)

    for tran in trans:
        soup = BeautifulSoup(tran, 'html.parser')

        days_ago = soup.find("div", {"aria-label": True}).get_text(strip=True)
        if "h" in days_ago or "m" in days_ago:
            date = datetime.now()
        elif "d" in days_ago:
            days_ago = int(days_ago[:-1])
            current_date = datetime.now()
            date = current_date - timedelta(days=days_ago + 1)
        elif re.match("[A-Za-z]{3}\s[0-9]{1,2},\s[0-9]{4}", days_ago):
            date = datetime.strptime(days_ago, '%b %d, %Y')
        else:
            date = datetime.strptime(
                days_ago + " " + datetime.now().strftime("%Y"), 
                '%b %d %Y',
            )

        story_headline = soup.select_one("div[id^='storyHeadlineId-']")\
            .get_text(strip=True)
        story_content = soup.select_one(".storyContent_storyContentLink__AiXaY")\
            .get_text(strip=True)

        if "Youpaid" in story_headline:
            name = story_content \
                + " - Venmo to " \
                + story_headline.replace("Youpaid", "")
            mult = -1
        elif "paidyou" in story_headline:
            name = story_content \
                + " - Venmo from " \
                + story_headline.replace("paidyou", "")
            mult = 1
        elif "Youcharged" in story_headline:
            name = story_content \
                + " - Venmo from " \
                + story_headline.replace("Youcharged", "")
            mult = 1
        elif "chargedyou" in story_headline:
            name = story_content \
                + " - Venmo to " \
                + story_headline.replace("chargedyou", "")
            mult = -1
        elif story_headline == "Standard Transfer Initiated":
            continue
        else:
            print("Venmo transaction \"" + story_headline \
                + "\" is unrecognized, please manually investigate")

        if "," in name:
            name = "\"" + name + "\""

        story_hidden_amount = soup.select_one("span[id^='storyHidenAmount-']")\
            .get_text(strip=True)
        amount = float(story_hidden_amount.replace("$", "")) * mult

        transactions.append(
            Transaction(date, name, amount)
        )

    return transactions

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
