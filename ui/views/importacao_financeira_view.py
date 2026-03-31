from pathlib import Path
import json
import shutil

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QPlainTextEdit, QTableWidget
)

from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem

class ImportacaoFinanceiraView(QWidget):
    def __init__(self, service, template_path):
        super().__init__()
        self.service = service
        self.template_path = Path(template_path)
        self._build_ui()
        self.reload_logs()

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("Importação Financeira Híbrida")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        root.addWidget(title)

        note = QLabel(
            "Modelo híbrido: a planilha padrão é a porta de entrada operacional, "
            "mas o sistema valida, importa e transforma os dados em base oficial."
        )
        note.setWordWrap(True)
        root.addWidget(note)

        buttons = QHBoxLayout()
        self.btn_template = QPushButton("Salvar cópia da planilha padrão")
        self.btn_template.clicked.connect(self.export_template)
        self.btn_validar = QPushButton("Validar planilha")
        self.btn_validar.clicked.connect(self.validate_file)
        self.btn_importar = QPushButton("Importar planilha")
        self.btn_importar.clicked.connect(self.import_file)
        for b in [self.btn_template, self.btn_validar, self.btn_importar]:
            buttons.addWidget(b)
        buttons.addStretch()
        root.addLayout(buttons)

        self.txt = QPlainTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setPlaceholderText("Resultado da validação/importação aparecerá aqui.")
        root.addWidget(self.txt, 1)

        root.addWidget(QLabel("Últimas importações"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Data", "Arquivo", "Status", "Resumo"])
        configure_table(self.table)
        root.addWidget(self.table, 1)

    def export_template(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar planilha padrão", "planilha_importacao_financeira_padrao.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"
        shutil.copyfile(self.template_path, path)
        QMessageBox.information(self, "Sucesso", f"Template salvo em:\n{path}")

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar planilha para validação/importação", "", "Excel (*.xlsx)"
        )
        return path

    def validate_file(self):
        path = self._pick_file()
        if not path:
            return
        try:
            result = self.service.validate_workbook(path)
            self._show_result(result, "Validação")
        except Exception as exc:
            QMessageBox.warning(self, "Erro", str(exc))

    def import_file(self):
        path = self._pick_file()
        if not path:
            return
        try:
            result = self.service.import_workbook(path)
            self._show_result(result, "Importação")
            self.reload_logs()
        except Exception as exc:
            QMessageBox.warning(self, "Erro", str(exc))

    def _show_result(self, result, titulo):
        lines = [f"{titulo}: {'OK' if result.get('ok') else 'ERROS'}", result.get("summary","")]
        counts = result.get("counts", {})
        if counts:
            lines.append("")
            lines.append("Linhas lidas por aba:")
            for k, v in counts.items():
                lines.append(f"- {k}: {v}")
        inserted = result.get("inserted")
        if inserted:
            lines.append("")
            lines.append("Registros processados:")
            for k, v in inserted.items():
                lines.append(f"- {k}: {v}")
        errors = result.get("errors", [])
        if errors:
            lines.append("")
            lines.append("Erros encontrados:")
            lines.extend([f"- {e}" for e in errors[:100]])
        self.txt.setPlainText("\n".join(lines))

    def reload_logs(self):
        rows = self.service.recent_logs()
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, TextItem(row["created_at"]))
            self.table.setItem(r, 1, TextItem(row["arquivo_nome"]))
            self.table.setItem(r, 2, TextItem(row["status"]))
            self.table.setItem(r, 3, TextItem(row["resumo"]))
