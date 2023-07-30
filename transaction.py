from datetime import datetime
from transaction_categories import categories, exclude_list, not_on_expense_budget_list

class Transaction:
    # accounted_for transactions are transactions whose expense is accounted for 
    # in some way separate from the budget, so they are flagged and not counted
    # towards the monthly budget expense totals
    def __init__(
            self, 
            datetime: datetime, 
            name: str, 
            amount: float, 
            on_expense_budget: bool = None):
        self.datetime = datetime
        self.name = name
        self.amount = amount
        self.category = "Misc"
        self.sub_category = "Misc"
        self.skip = False

        # determine if this transaction should be excluded
        for ex in exclude_list:
            if ex in self.name:
                self.skip = True
                break

        # categorize this transaction
        if not self.skip:
            for cat in categories:
                for sub_cat in categories[cat]:
                    for title in categories[cat][sub_cat]:
                        if title.lower() in self.name.lower():
                            self.category = cat
                            self.sub_category = sub_cat
                            break
        
        # set if the transaction is included on the expense budget
        if on_expense_budget is None:
            self.on_expense_budget = True
            for cat in not_on_expense_budget_list:
                if cat == self.category:
                    self.on_expense_budget = False
                    break
        else:
            self.on_expense_budget = on_expense_budget

    def get_date_str(self):
        return self.datetime.strftime('%m/%d/%Y')

    def get_month_id(self):
        return self.datetime.strftime('%Y%m')
    
    def get_month(self):
        return self.datetime.strftime('%m')

    def get_dollar_str(self):
        return ("-" if self.amount < 0 else "") \
            + "${:.2f}".format(abs(self.amount))

    def get_formatted_transaction(self):
        if self.skip:
            return ""
        return f"{self.get_month_id()}," \
            + f"{self.get_date_str()}," \
            + f"{self.name}," \
            + f"{self.get_dollar_str()}," \
            + f"{self.category}," \
            + f"{self.sub_category}," \
            + f"{'Yes' if self.on_expense_budget else 'No'}\n"