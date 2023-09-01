from datetime import datetime
from transaction_categories import categories, exclude_list, not_on_expense_budget_list
import re

class Transaction:
    def __init__(
            self, 
            datetime: datetime, 
            name: str, 
            amount: float, 
            transaction_type: str = None):
        self.datetime = datetime
        self.name = name
        self.amount = amount
        self.category = "Misc"
        self.sub_category = "Misc"
        self.skip = False

        # determine if this transaction should be excluded
        self.__determine_exclusion()

        # categorize this transaction
        self.__categorize()
        
        # add a type to this transaction
        if not transaction_type:
            self.__set_type()
        else:
            self.transaction_type = transaction_type

    def __determine_exclusion(self):
        for ex in exclude_list:
            if re.match(ex, self.name):
                self.skip = True
                return

    def __categorize(self):
        if not self.skip:
            for cat in categories:
                for sub_cat in categories[cat]:
                    for title in categories[cat][sub_cat]:
                        if re.search(title.lower(), self.name.lower()):
                            self.category = cat
                            self.sub_category = sub_cat
                            return

    def __set_type(self):
        self.transaction_type = "Expense"
        for cat in not_on_expense_budget_list:
            if cat == self.category:
                self.transaction_type = "External"
                return

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
            + f"{self.transaction_type}\n"