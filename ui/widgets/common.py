from PySide6.QtWidgets import QHeaderView, QLabel, QHBoxLayout, QTableWidgetItem
from PySide6.QtGui import QDoubleValidator, QIntValidator, QColor

STATUS_STYLE = {
    "rascunho": ("#f3f4f6", "#374151"),
    "revisado": ("#dbeafe", "#1d4ed8"),
    "aprovado": ("#dcfce7", "#166534"),
    "fechado": ("#e5e7eb", "#111827"),
    "divergente": ("#fee2e2", "#b91c1c"),
    "em_aprovacao": ("#fef3c7", "#92400e"),
    "aberta": ("#fef3c7", "#92400e"),
}

def configure_table(table):
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Interactive)
    header.setStretchLastSection(True)
    table.setSortingEnabled(True)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
    table.setSelectionMode(table.SelectionMode.SingleSelection)
    table.setEditTriggers(table.EditTrigger.NoEditTriggers)


def status_labels_layout():
    layout = QHBoxLayout()
    labels = []
    for text in ["Registros: 0", "Indicador 1: -", "Indicador 2: -", "Filtro: não"]:
        lbl = QLabel(text)
        lbl.setStyleSheet("padding:4px 8px; border:1px solid #d0d0d0; border-radius:6px; background:#fafafa;")
        layout.addWidget(lbl)
        labels.append(lbl)
    layout.addStretch()
    return layout, labels


def apply_float_validator(widget, max_value=999999999999.99, decimals=4):
    val = QDoubleValidator(0.0, max_value, decimals, widget)
    widget.setValidator(val)


def apply_int_validator(widget, max_value=999999999):
    val = QIntValidator(0, max_value, widget)
    widget.setValidator(val)


def make_status_item(status):
    text = str(status or "").strip() or "-"
    item = QTableWidgetItem(text)
    bg, fg = STATUS_STYLE.get(text.lower(), ("#f9fafb", "#374151"))
    item.setBackground(QColor(bg))
    item.setForeground(QColor(fg))
    return item


def friendly_error(exc: Exception) -> str:
    msg = str(exc).strip() or exc.__class__.__name__
    replacements = {
        'UNIQUE constraint failed': 'Já existe um registro igual.',
        'FOREIGN KEY constraint failed': 'Há dependências relacionadas; revise o vínculo informado.',
        'not null': 'Existe campo obrigatório sem preenchimento.',
    }
    for old, new in replacements.items():
        if old.lower() in msg.lower():
            return new + f"\n\nDetalhe técnico: {msg}"
    return msg
