from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QMessageBox, QComboBox
)

class LoginView(QWidget):
    login_success = Signal(int)

    def __init__(self, usuario_repo):
        super().__init__()
        self.usuario_repo = usuario_repo
        self._build_ui()
        self.reload_users()

    def _build_ui(self):
        self.setStyleSheet(
            '''
            QWidget { background: #f4f7fb; }
            QFrame#card {
                background: white;
                border: 1px solid #d9e2ef;
                border-radius: 14px;
            }
            QLabel#title {
                font-size: 28px;
                font-weight: 800;
                color: #133a63;
            }
            QLabel#subtitle {
                font-size: 13px;
                color: #5c6f82;
            }
            QLabel#logo {
                font-size: 30px;
                font-weight: 900;
                color: #0f4c81;
                letter-spacing: 1px;
            }
            QLabel#logo2 {
                font-size: 14px;
                font-weight: 600;
                color: #406280;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 1px solid #bfd0e0;
                border-radius: 8px;
                background: white;
            }
            QPushButton {
                padding: 10px 16px;
                border-radius: 8px;
                background: #0f4c81;
                color: white;
                font-weight: 700;
            }
            QPushButton:hover { background: #0c3e69; }
            '''
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)

        root.addStretch()

        center = QHBoxLayout()
        center.addStretch()

        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(520)

        box = QVBoxLayout(card)
        box.setContentsMargins(28, 28, 28, 28)
        box.setSpacing(12)

        logo = QLabel("NAEST")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignCenter)
        box.addWidget(logo)

        logo2 = QLabel("Consultoria e Engenharia")
        logo2.setObjectName("logo2")
        logo2.setAlignment(Qt.AlignCenter)
        box.addWidget(logo2)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#d9e2ef;")
        box.addWidget(sep)

        title = QLabel("Sistema Integrado de Gestão de Contratos, Medições e Produtividade")
        title.setObjectName("title")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        box.addWidget(title)

        subtitle = QLabel("Acesse com seu usuário para entrar no ambiente de acompanhamento técnico, financeiro e de aprovações.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        box.addWidget(subtitle)

        box.addSpacing(10)

        lbl_user = QLabel("Usuário")
        box.addWidget(lbl_user)
        self.cb_usuario = QComboBox()
        box.addWidget(self.cb_usuario)

        lbl_email = QLabel("Confirmação de email")
        box.addWidget(lbl_email)
        self.ed_email = QLineEdit()
        self.ed_email.setPlaceholderText("Digite o email cadastrado")
        box.addWidget(self.ed_email)

        actions = QHBoxLayout()
        actions.addStretch()
        self.btn_login = QPushButton("Entrar no sistema")
        self.btn_login.clicked.connect(self.do_login)
        actions.addWidget(self.btn_login)
        box.addLayout(actions)

        note = QLabel("Ambiente interno NAEST • Controle de contratos, planejamento, medições, workflow e dashboard executivo")
        note.setObjectName("subtitle")
        note.setAlignment(Qt.AlignCenter)
        note.setWordWrap(True)
        box.addWidget(note)

        center.addWidget(card)
        center.addStretch()

        root.addLayout(center)
        root.addStretch()

    def reload_users(self):
        current = self.cb_usuario.currentData()
        self.cb_usuario.clear()
        for u in self.usuario_repo.list_all():
            if int(u["ativo"] or 0) == 1:
                self.cb_usuario.addItem(f'{u["nome"]} - {u["perfil"]}', u["id"])
                self.cb_usuario.setItemData(self.cb_usuario.count()-1, u["email"], Qt.UserRole + 1)
        idx = self.cb_usuario.findData(current)
        self.cb_usuario.setCurrentIndex(idx if idx >= 0 and self.cb_usuario.count() > 0 else 0)

    def do_login(self):
        uid = self.cb_usuario.currentData()
        if uid is None:
            QMessageBox.warning(self, "Atenção", "Não há usuários ativos cadastrados.")
            return
        email_in = self.ed_email.text().strip().lower()
        email_ok = str(self.cb_usuario.currentData(Qt.UserRole + 1) or "").strip().lower()
        if email_in != email_ok:
            QMessageBox.warning(self, "Atenção", "Email não confere com o usuário selecionado.")
            return
        self.login_success.emit(int(uid))
