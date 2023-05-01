from transaction import Transaction

def split_naku_income(original_transaction: Transaction):
    if not "NAKUPUNA SOLUTIO" == original_transaction.name:
        return []
    
    original_transaction.amount += 13
    
    return [
        Transaction(original_transaction.datetime, "HDS Dental Insurance", -13),
        original_transaction,
    ]

def split_digitalocean_invoice(original_transaction: Transaction):
    if not "Digitalocean.com" == original_transaction.name:
        return []
    
    trans = [
        Transaction(original_transaction.datetime, "Romanius", -6),
        Transaction(original_transaction.datetime, "Analysis Droplet", -57),
        Transaction(original_transaction.datetime, "Live Droplet", -21),
    ]

    expected_server_costs = -84

    if expected_server_costs != original_transaction.amount:
        original_transaction.amount += -expected_server_costs
        trans.append(original_transaction)

    return trans

def split_rent_utilities(original_transaction: Transaction):
    if not "Buttonwood Oper" == original_transaction.name:
        return []
    
    rent_amount = -1303
    utilties_amount = -(rent_amount + -original_transaction.amount)

    original_transaction.amount = rent_amount

    return[
        Transaction(original_transaction.datetime, "Bundled Utilites", utilties_amount),
        original_transaction,
    ]

hooks = [
    split_naku_income,
    split_digitalocean_invoice,
    split_rent_utilities,
]