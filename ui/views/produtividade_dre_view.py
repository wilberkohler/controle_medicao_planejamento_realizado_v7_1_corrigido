from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QMessageBox, QFileDialog, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem, FloatItem

class ProdutividadeDREView(QWidget):
    def __init__(self, analytics_service, parametros_service):
        super().__init__(); self.analytics_service=analytics_service; self.parametros_service=parametros_service; self.rows_cache=[]; self.composicao_cache=[]; self._bar_meta_1=[]; self._bar_meta_2=[]; self._build_ui(); self.reload_data()
    def _build_ui(self):
        root=QVBoxLayout(self); title=QLabel('DRE Gerencial'); title.setStyleSheet('font-size:18px;font-weight:700;'); root.addWidget(title)
        top=QHBoxLayout(); top.addWidget(QLabel('Visão:')); self.cb_visao=QComboBox(); self.cb_visao.addItems(['estrutural','mensal por competência']); self.cb_visao.currentIndexChanged.connect(self.reload_data); top.addWidget(self.cb_visao); top.addWidget(QLabel('Nível:')); self.cb_nivel=QComboBox(); self.cb_nivel.addItems(['contrato','etapa','grupo']); self.cb_nivel.currentIndexChanged.connect(self.reload_data); top.addWidget(self.cb_nivel); top.addWidget(QLabel('Contrato (opcional):')); self.cb_contrato=QComboBox(); self.cb_contrato.currentIndexChanged.connect(self.reload_data); top.addWidget(self.cb_contrato); top.addWidget(QLabel('Imposto sobre o faturamento (%):')); self.ed_imposto=QLineEdit(); self.ed_imposto.setMaximumWidth(120); top.addWidget(self.ed_imposto); self.btn_aplicar=QPushButton('Aplicar'); self.btn_aplicar.clicked.connect(self.aplicar_parametro); top.addWidget(self.btn_aplicar); self.btn_exportar=QPushButton('Exportar CSV'); self.btn_exportar.clicked.connect(self.exportar_csv); top.addWidget(self.btn_exportar); self.btn_limpar=QPushButton('Limpar detalhe'); self.btn_limpar.clicked.connect(self.clear_detail); top.addWidget(self.btn_limpar); top.addStretch(); root.addLayout(top)
        cards=QHBoxLayout(); self.lbl_rb=self._card('Receita Bruta','0,00'); self.lbl_ded=self._card('Deduções / Impostos','0,00'); self.lbl_rl=self._card('Receita Líquida','0,00'); self.lbl_dg=self._card('Despesas Gerais','0,00'); self.lbl_ct=self._card('Custo Total','0,00'); self.lbl_mo=self._card('Margem Operacional','0,00'); [cards.addWidget(c) for c in [self.lbl_rb,self.lbl_ded,self.lbl_rl,self.lbl_dg,self.lbl_ct,self.lbl_mo]]; root.addLayout(cards)
        self.lbl_hint=QLabel('Clique em uma barra do gráfico para filtrar a tabela e, na visão mensal, abrir a composição da competência.'); self.lbl_hint.setWordWrap(True); self.lbl_hint.setStyleSheet('color:#555;'); root.addWidget(self.lbl_hint)
        charts=QHBoxLayout(); self.fig1=Figure(figsize=(6,3.2)); self.canvas1=FigureCanvas(self.fig1); self.fig2=Figure(figsize=(6,3.2)); self.canvas2=FigureCanvas(self.fig2); charts.addWidget(self.canvas1); charts.addWidget(self.canvas2); root.addLayout(charts)
        root.addWidget(QLabel('Estrutura gerencial do DRE')); self.table=QTableWidget(0,15); self.table.setHorizontalHeaderLabels(['Referência','Nome/Ref.','Receita Prevista','Receita Bruta','Deduções/Impostos','Receita Líquida','Custo Equipe','Custo Terceiros','Despesas Gerais','Custo Total','Margem Bruta','Margem Operacional','Imp. %','MB %','MO %']); configure_table(self.table); root.addWidget(self.table)
        root.addWidget(QLabel('Composição do detalhe selecionado')); self.table_det=QTableWidget(0,7); self.table_det.setHorizontalHeaderLabels(['Referência','Nome','Receita Prevista','Receita Bruta','Custo Equipe','Custo Terceiros','Despesas Gerais']); configure_table(self.table_det); root.addWidget(self.table_det)
        self.canvas1.mpl_connect('button_press_event', self.on_revenue_click); self.canvas1.mpl_connect('motion_notify_event', self.on_revenue_hover); self.canvas2.mpl_connect('button_press_event', self.on_margin_click); self.canvas2.mpl_connect('motion_notify_event', self.on_margin_hover)
    def _card(self,t,v):
        lbl=QLabel(f"{t}\n{v}"); lbl.setStyleSheet('border:1px solid #cccccc; border-radius:8px; padding:10px; font-size:14px; background:#f8f8f8;'); return lbl
    def _fmt(self,v):
        try: return f"{float(v):,.2f}".replace(',', 'X').replace('.', ',').replace('X','.')
        except Exception: return str(v)
    def clear_detail(self): self.composicao_cache=[]; self.table_det.setRowCount(0); self.lbl_hint.setText('Clique em uma barra do gráfico para filtrar a tabela e, na visão mensal, abrir a composição da competência.')
    def reload_data(self):
        cur=self.cb_contrato.currentData(); self.cb_contrato.blockSignals(True); self.cb_contrato.clear(); self.cb_contrato.addItem('Todos', None)
        for c in self.analytics_service.contratos(): self.cb_contrato.addItem(f"{c['codigo']} - {c['nome']}", c['id'])
        idx=self.cb_contrato.findData(cur); self.cb_contrato.setCurrentIndex(idx if idx>=0 else 0); self.cb_contrato.blockSignals(False)
        param=self.parametros_service.get_ativo(); imposto=float(param['imposto_percentual'] or 16.8); self.ed_imposto.setText(self._fmt(imposto))
        visao=self.cb_visao.currentText(); self.cb_nivel.setEnabled(visao=='estrutural'); contrato_id=self.cb_contrato.currentData()
        if visao=='mensal por competência': rows=self.analytics_service.dre_mensal_competencia(imposto, contrato_id); ref_key='competencia'; name_key=''; title_suffix='mensal'
        else: nivel=self.cb_nivel.currentText(); rows=self.analytics_service.dre_gerencial_por_nivel(nivel, imposto, contrato_id); ref_key='nivel_codigo'; name_key='nivel_nome'; title_suffix=f'por {nivel}'
        self.rows_cache=rows; rb=sum(r['receita_bruta'] if 'receita_bruta' in r else r['receita_faturada'] for r in rows); ded=sum(r['deducoes_impostos'] if 'deducoes_impostos' in r else r['impostos_sobre_faturamento'] for r in rows); rl=sum(r['receita_liquida'] for r in rows); dg=sum(r.get('despesas_gerais',0) for r in rows); ct=sum(r['custo_total'] for r in rows); mo=sum(r['margem_operacional'] for r in rows)
        self.lbl_rb.setText(f"Receita Bruta\n{self._fmt(rb)}"); self.lbl_ded.setText(f"Deduções / Impostos\n{self._fmt(ded)}"); self.lbl_rl.setText(f"Receita Líquida\n{self._fmt(rl)}"); self.lbl_dg.setText(f"Despesas Gerais\n{self._fmt(dg)}"); self.lbl_ct.setText(f"Custo Total\n{self._fmt(ct)}"); self.lbl_mo.setText(f"Margem Operacional\n{self._fmt(mo)}")
        self.table.setRowCount(0)
        for row in rows:
            r=self.table.rowCount(); self.table.insertRow(r); self.table.setItem(r,0,TextItem(row.get(ref_key,''))); self.table.setItem(r,1,TextItem(row.get(name_key,''))); self.table.setItem(r,2,CurrencyItem(row['receita_prevista'])); rbv=row['receita_bruta'] if 'receita_bruta' in row else row['receita_faturada']; dedv=row['deducoes_impostos'] if 'deducoes_impostos' in row else row['impostos_sobre_faturamento']; self.table.setItem(r,3,CurrencyItem(rbv)); self.table.setItem(r,4,CurrencyItem(dedv)); self.table.setItem(r,5,CurrencyItem(row['receita_liquida'])); self.table.setItem(r,6,CurrencyItem(row['custo_equipe'])); self.table.setItem(r,7,CurrencyItem(row['custo_terceiros'])); self.table.setItem(r,8,CurrencyItem(row.get('despesas_gerais',0))); self.table.setItem(r,9,CurrencyItem(row['custo_total'])); self.table.setItem(r,10,CurrencyItem(row['margem_bruta'])); self.table.setItem(r,11,CurrencyItem(row['margem_operacional'])); self.table.setItem(r,12,FloatItem(row['imposto_percentual'],2)); mb_pct=row.get('margem_percentual', (row['margem_bruta']/rbv*100.0) if rbv else 0.0); mo_pct=row.get('margem_liquida_percentual', (row['margem_operacional']/rbv*100.0) if rbv else 0.0); self.table.setItem(r,13,FloatItem(mb_pct,2)); self.table.setItem(r,14,FloatItem(mo_pct,2))
        self._plot_receita(rows, title_suffix, ref_key); self._plot_margens(rows, title_suffix, ref_key)
    def _plot_receita(self, rows, suffix, ref_key):
        self.fig1.clear(); ax=self.fig1.add_subplot(111); labels=[r.get(ref_key,'') for r in rows[:15]]; rb=[r['receita_bruta'] if 'receita_bruta' in r else r['receita_faturada'] for r in rows[:15]]; ded=[r['deducoes_impostos'] if 'deducoes_impostos' in r else r['impostos_sobre_faturamento'] for r in rows[:15]]; rl=[r['receita_liquida'] for r in rows[:15]]; x=list(range(len(labels))); b1=ax.bar([i-0.25 for i in x], rb, width=0.25, label='Receita Bruta'); b2=ax.bar([i for i in x], ded, width=0.25, label='Deduções'); b3=ax.bar([i+0.25 for i in x], rl, width=0.25, label='Receita Líquida'); self._bar_meta_1=[]
        for i,row in enumerate(rows[:15]): self._bar_meta_1 += [(b1[i], labels[i], {'receita_bruta':rb[i],'deducoes':ded[i],'receita_liquida':rl[i],'margem':row['margem_operacional']}), (b2[i], labels[i], {'receita_bruta':rb[i],'deducoes':ded[i],'receita_liquida':rl[i],'margem':row['margem_operacional']}), (b3[i], labels[i], {'receita_bruta':rb[i],'deducoes':ded[i],'receita_liquida':rl[i],'margem':row['margem_operacional']})]
        ax.set_title(f'Estrutura de receita {suffix}'); ax.set_xticks(x); ax.set_xticklabels(labels, rotation=35, ha='right'); ax.grid(True, axis='y', alpha=0.3); ax.legend(); self.fig1.tight_layout(); self.canvas1.draw()
    def _plot_margens(self, rows, suffix, ref_key):
        self.fig2.clear(); ax=self.fig2.add_subplot(111); labels=[r.get(ref_key,'') for r in rows[:15]]; mb=[r['margem_bruta'] for r in rows[:15]]; mo=[r['margem_operacional'] for r in rows[:15]]; x=list(range(len(labels))); b1=ax.bar([i-0.2 for i in x], mb, width=0.4, label='Margem Bruta'); b2=ax.bar([i+0.2 for i in x], mo, width=0.4, label='Margem Operacional'); self._bar_meta_2=[]
        for i,row in enumerate(rows[:15]): rbv=row['receita_bruta'] if 'receita_bruta' in row else row['receita_faturada']; dedv=row['deducoes_impostos'] if 'deducoes_impostos' in row else row['impostos_sobre_faturamento']; desvio=((rbv-row['receita_prevista'])/(row['receita_prevista'] or 1)*100) if row['receita_prevista'] else 0; self._bar_meta_2 += [(b1[i], labels[i], {'receita_bruta':rbv,'custo':row['custo_total'],'imposto':dedv,'margem':mb[i],'desvio_pct':desvio}), (b2[i], labels[i], {'receita_bruta':rbv,'custo':row['custo_total'],'imposto':dedv,'margem':mo[i],'desvio_pct':desvio})]
        ax.set_title(f'Margem bruta x operacional {suffix}'); ax.set_xticks(x); ax.set_xticklabels(labels, rotation=35, ha='right'); ax.grid(True, axis='y', alpha=0.3); ax.legend(); self.fig2.tight_layout(); self.canvas2.draw()
    def _fill_composicao(self, rows):
        self.table_det.setRowCount(0)
        for row in rows:
            r=self.table_det.rowCount(); self.table_det.insertRow(r); self.table_det.setItem(r,0,TextItem(row.get('referencia',''))); self.table_det.setItem(r,1,TextItem(row.get('nome',''))); self.table_det.setItem(r,2,CurrencyItem(row.get('receita_prevista',0))); self.table_det.setItem(r,3,CurrencyItem(row.get('receita_bruta',0))); self.table_det.setItem(r,4,CurrencyItem(row.get('custo_equipe',0))); self.table_det.setItem(r,5,CurrencyItem(row.get('custo_terceiros',0))); self.table_det.setItem(r,6,CurrencyItem(row.get('despesas_gerais',0)))
    def _detail_for_ref(self, ref):
        visao=self.cb_visao.currentText(); contrato_id=self.cb_contrato.currentData()
        if visao=='mensal por competência': self.composicao_cache=self.analytics_service.dre_mensal_composicao(ref, contrato_id); self.lbl_hint.setText(f'Competência {ref} | composição aberta por contrato.')
        else: self.composicao_cache=[{'referencia':r.get('nivel_codigo',''),'nome':r.get('nivel_nome',''),'receita_prevista':r['receita_prevista'],'receita_bruta':r.get('receita_bruta',r.get('receita_faturada',0)),'custo_equipe':r['custo_equipe'],'custo_terceiros':r['custo_terceiros'],'despesas_gerais':r.get('despesas_gerais',0)} for r in self.rows_cache if r.get('nivel_codigo','')==ref]; self.lbl_hint.setText(f'Referência {ref} selecionada no DRE estrutural.')
        self._fill_composicao(self.composicao_cache)
    def on_revenue_click(self,event):
        if event.inaxes is None: return
        for patch, ref, payload in self._bar_meta_1:
            contains,_=patch.contains(event)
            if contains: self._detail_for_ref(ref); return
    def on_revenue_hover(self,event):
        if event.inaxes is None: return
        for patch, ref, payload in self._bar_meta_1:
            contains,_=patch.contains(event)
            if contains: self.lbl_hint.setText(f"{ref} | receita bruta {self._fmt(payload['receita_bruta'])} | deduções {self._fmt(payload['deducoes'])} | receita líquida {self._fmt(payload['receita_liquida'])} | margem {self._fmt(payload['margem'])}"); return
    def on_margin_click(self,event):
        if event.inaxes is None: return
        for patch, ref, payload in self._bar_meta_2:
            contains,_=patch.contains(event)
            if contains: self._detail_for_ref(ref); return
    def on_margin_hover(self,event):
        if event.inaxes is None: return
        for patch, ref, payload in self._bar_meta_2:
            contains,_=patch.contains(event)
            if contains: self.lbl_hint.setText(f"{ref} | receita {self._fmt(payload['receita_bruta'])} | custo {self._fmt(payload['custo'])} | imposto {self._fmt(payload['imposto'])} | margem {self._fmt(payload['margem'])} | desvio {payload['desvio_pct']:.1f}%"); return
    def aplicar_parametro(self):
        try: self.parametros_service.set_percentual(self.ed_imposto.text()); QMessageBox.information(self,'Sucesso','Parâmetro de imposto atualizado.'); self.reload_data()
        except Exception as exc: QMessageBox.warning(self,'Atenção',str(exc))
    def exportar_csv(self):
        path,_=QFileDialog.getSaveFileName(self,'Salvar DRE','dre_gerencial.csv','CSV (*.csv)')
        if not path: return
        if not path.lower().endswith('.csv'): path += '.csv'
        try:
            with open(path,'w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f, delimiter=';'); w.writerow(['Referência','Nome/Ref.','Receita Prevista','Receita Bruta','Deduções/Impostos','Receita Líquida','Custo Equipe','Custo Terceiros','Despesas Gerais','Custo Total','Margem Bruta','Margem Operacional','Imposto %','MB %','MO %'])
                for row in self.rows_cache:
                    rb=row['receita_bruta'] if 'receita_bruta' in row else row['receita_faturada']; ded=row['deducoes_impostos'] if 'deducoes_impostos' in row else row['impostos_sobre_faturamento']; mb_pct=row.get('margem_percentual', (row['margem_bruta']/rb*100.0) if rb else 0.0); mo_pct=row.get('margem_liquida_percentual', (row['margem_operacional']/rb*100.0) if rb else 0.0); ref=row.get('competencia', row.get('nivel_codigo','')); nome=row.get('nivel_nome',''); w.writerow([ref,nome,row['receita_prevista'],rb,ded,row['receita_liquida'],row['custo_equipe'],row['custo_terceiros'],row.get('despesas_gerais',0),row['custo_total'],row['margem_bruta'],row['margem_operacional'],row['imposto_percentual'],mb_pct,mo_pct])
            QMessageBox.information(self,'Sucesso',f'DRE exportado para:\n{path}')
        except Exception as exc: QMessageBox.warning(self,'Erro',str(exc))
