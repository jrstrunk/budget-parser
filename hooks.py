from transaction import Transaction

def split_naku_income(original_transaction: Transaction):
    if not "NAKUPUNA SOLUTIO" == original_transaction.name:
        return [] # do not modify original transaction
    
    original_transaction.amount += 10.50
    
    return [
        Transaction(original_transaction.datetime, "HDS Dental Insurance", -10.50),
        original_transaction,
    ]

def split_digitalocean_invoice(original_transaction: Transaction):
    if not "Digitalocean.com" == original_transaction.name:
        return [] # do not modify original transaction

    original_transaction.name = "Digitalocean.com - Investment Business Servers"

    return [
        original_transaction,
    ]

def split_rent_utilities(original_transaction: Transaction):
    if not "RPMANAGEMENT-BGO" == original_transaction.name:
        return [] # do not modify original transaction
    
    rent_amount = -1303
    utilties_amount = -(rent_amount + -original_transaction.amount)

    original_transaction.amount = rent_amount

    return[
        Transaction(original_transaction.datetime, "Bundled Utilites", utilties_amount),
        original_transaction,
    ]

def split_spotify_plan_gift(original_transaction: Transaction):
    if not original_transaction.name == "Spotify usa":
        return [] # do not modify original transaction
    
    duo_plan_cost = -14.99
    gift_plan_cost = original_transaction.amount - duo_plan_cost
    
    original_transaction.amount = duo_plan_cost

    return [
        Transaction(original_transaction.datetime, "Spotify usa - Family Christmas Gift", gift_plan_cost, False),
        original_transaction,
    ]

hooks = [
    split_naku_income,
    split_spotify_plan_gift,
]