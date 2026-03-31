from PySide6.QtWidgets import QTableWidgetItem
from utils.number_utils import br_number
from utils.date_utils import parse_date

class TextItem(QTableWidgetItem):
    def __init__(self, text=""):
        super().__init__(str(text))

class IntegerItem(QTableWidgetItem):
    def __init__(self, value=0):
        self.sort_value = int(value or 0)
        super().__init__(str(self.sort_value))
    def __lt__(self, other):
        if isinstance(other, IntegerItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)

class FloatItem(QTableWidgetItem):
    def __init__(self, value=0.0, decimals=2):
        self.sort_value = float(value or 0)
        super().__init__(br_number(self.sort_value, decimals))
    def __lt__(self, other):
        if isinstance(other, FloatItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)

class CurrencyItem(FloatItem):
    pass

class DateItem(QTableWidgetItem):
    def __init__(self, value=""):
        self.raw = str(value or "")
        self.sort_value = parse_date(self.raw)
        super().__init__(self.raw)
    def __lt__(self, other):
        if isinstance(other, DateItem):
            a, b = self.sort_value, other.sort_value
            if a is None and b is None: return False
            if a is None: return True
            if b is None: return False
            return a < b
        return super().__lt__(other)
