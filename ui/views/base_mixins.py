class FilterMixin:
    def apply_text_filter(self, table, text):
        text = str(text or "").strip().lower()
        for row in range(table.rowCount()):
            visible = False
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            table.setRowHidden(row, not visible)
