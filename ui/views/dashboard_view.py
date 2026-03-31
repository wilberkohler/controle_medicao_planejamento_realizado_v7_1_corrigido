from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QTableWidget, QComboBox, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.widgets.common import configure_table
from ui.widgets.table_items import TextItem, CurrencyItem
import csv

class DashboardView(QWidget):
    def __init__(self, service):
        super().__init__(); self.service=service
        self.rows_cache=[]; self.stages_cache=[]; self.aprov_cache={}
        self._contract_bar_map=[]; self._curve_point_map=[]; self._stage_bar_map=[]
        self._heatmap_meta={"xlabels":[],"ylabels":[],"matrix":[],"level":"contrato"}
        self.current_filters={"contrato_id":None,"etapa_codigo":None,"grupo_codigo":None,"competencia":None}
        self._build_ui(); self.reload_data()
    def _build_ui(self):
        root=QVBoxLayout(self)
        title=QLabel("Dashboard executivo"); title.setStyleSheet("font-size:20px;font-weight:700;"); root.addWidget(title)
        top=QHBoxLayout(); left=QVBoxLayout(); left.addWidget(QLabel("Contratos considerados"))
        self.list_contratos=QListWidget(); self.list_contratos.setMaximumHeight(120); self.list_contratos.itemChanged.connect(self.refresh_from_selection); left.addWidget(self.list_contratos)
        btns=QHBoxLayout();
        self.btn_todos=QPushButton("Marcar todos"); self.btn_todos.clicked.connect(self.marcar_todos)
        self.btn_nenhum=QPushButton("Desmarcar todos"); self.btn_nenhum.clicked.connect(self.desmarcar_todos)
        self.btn_limpar=QPushButton("Limpar drill-down"); self.btn_limpar.clicked.connect(self.clear_drilldown)
        for b in [self.btn_todos,self.btn_nenhum,self.btn_limpar]: btns.addWidget(b)
        btns.addStretch(); left.addLayout(btns); top.addLayout(left,2)
        cards=QHBoxLayout();
        self.lbl_contratos=self._card("Contratos","0"); self.lbl_prev=self._card("Previsto","0,00"); self.lbl_real=self._card("Realizado","0,00"); self.lbl_saldo=self._card("Saldo","0,00"); self.lbl_pend=self._card("Em aprovação","0"); self.lbl_aprov=self._card("Aprovados","0")
        for w in [self.lbl_contratos,self.lbl_prev,self.lbl_real,self.lbl_saldo,self.lbl_pend,self.lbl_aprov]: cards.addWidget(w)
        top.addLayout(cards,3); root.addLayout(top)
        opts=QHBoxLayout(); opts.addWidget(QLabel("Visão de etapas:")); self.cb_stage_mode=QComboBox(); self.cb_stage_mode.addItems(["Previsto x Realizado","Saldo"]); self.cb_stage_mode.currentIndexChanged.connect(self.refresh_from_selection); opts.addWidget(self.cb_stage_mode); opts.addWidget(QLabel("Heatmap:")); self.cb_heatmap_mode=QComboBox(); self.cb_heatmap_mode.addItems(["Contrato","Etapa","Grupo"]); self.cb_heatmap_mode.currentIndexChanged.connect(self.refresh_from_selection); opts.addWidget(self.cb_heatmap_mode)
        self.btn_export_png=QPushButton("Exportar dashboard PNG"); self.btn_export_png.clicked.connect(self.export_dashboard_png); self.btn_export_csv=QPushButton("Exportar detalhe CSV"); self.btn_export_csv.clicked.connect(self.export_detail_csv); opts.addWidget(self.btn_export_png); opts.addWidget(self.btn_export_csv); opts.addStretch(); root.addLayout(opts)
        self.lbl_hint=QLabel("Interação: clique em contrato, mês, etapa ou heatmap para filtrar o detalhe."); self.lbl_hint.setWordWrap(True); self.lbl_hint.setStyleSheet("color:#555;"); root.addWidget(self.lbl_hint)
        row1=QHBoxLayout(); self.fig1=Figure(figsize=(6,3.2)); self.canvas1=FigureCanvas(self.fig1); self.fig2=Figure(figsize=(5,3.2)); self.canvas2=FigureCanvas(self.fig2); row1.addWidget(self.canvas1,3); row1.addWidget(self.canvas2,2); root.addLayout(row1)
        row2=QHBoxLayout(); self.fig3=Figure(figsize=(6,3.2)); self.canvas3=FigureCanvas(self.fig3); self.fig4=Figure(figsize=(5,3.2)); self.canvas4=FigureCanvas(self.fig4); row2.addWidget(self.canvas3,3); row2.addWidget(self.canvas4,2); root.addLayout(row2)
        row3=QHBoxLayout(); self.fig5=Figure(figsize=(8.5,3.4)); self.canvas5=FigureCanvas(self.fig5); row3.addWidget(self.canvas5,1); root.addLayout(row3)
        root.addWidget(QLabel("Detalhe filtrado / drill-down")); self.table_dev=QTableWidget(0,8); self.table_dev.setHorizontalHeaderLabels(["Contrato","Etapa","Grupo","Entregável","Competência","Previsto","Realizado","Saldo"]); configure_table(self.table_dev); root.addWidget(self.table_dev)
        self.canvas1.mpl_connect("button_press_event", self.on_curve_click); self.canvas1.mpl_connect("motion_notify_event", self.on_curve_hover)
        self.canvas3.mpl_connect("button_press_event", self.on_contract_chart_click); self.canvas3.mpl_connect("motion_notify_event", self.on_contract_chart_hover)
        self.canvas4.mpl_connect("button_press_event", self.on_stage_chart_click); self.canvas4.mpl_connect("motion_notify_event", self.on_stage_chart_hover)
        self.canvas5.mpl_connect("button_press_event", self.on_heatmap_click); self.canvas5.mpl_connect("motion_notify_event", self.on_heatmap_hover)
    def _card(self,t,v):
        lbl=QLabel(f"{t}\n{v}"); lbl.setStyleSheet("border:1px solid #cccccc; border-radius:8px; padding:10px; font-size:14px; background:#f8f8f8;"); lbl.setMinimumWidth(150); return lbl
    def reload_data(self):
        self.rows_cache=list(self.service.dashboard_contracts_detail() or []); self.stages_cache=list(self.service.dashboard_stage_detail(None) or []); self.aprov_cache=dict(self.service.aprovacoes_resumo() or {})
        self.list_contratos.blockSignals(True); self.list_contratos.clear()
        for row in self.rows_cache:
            item=QListWidgetItem(f"{row['contrato_codigo']} - {row['contrato_nome']}"); item.setFlags(item.flags() | Qt.ItemIsUserCheckable); item.setCheckState(Qt.Checked); item.setData(Qt.UserRole,row['contrato_id']); self.list_contratos.addItem(item)
        self.list_contratos.blockSignals(False); self.clear_drilldown(refresh=True)
    def selecionados(self):
        return [self.list_contratos.item(i).data(Qt.UserRole) for i in range(self.list_contratos.count()) if self.list_contratos.item(i).checkState()==Qt.Checked]
    def clear_drilldown(self, refresh=True):
        self.current_filters={"contrato_id":None,"etapa_codigo":None,"grupo_codigo":None,"competencia":None}; self.lbl_hint.setText("Interação: clique em contrato, mês, etapa ou heatmap para filtrar o detalhe.")
        if refresh: self.refresh_from_selection()
    def refresh_from_selection(self):
        selected_ids=set(self.selecionados()); rows=[r for r in self.rows_cache if r['contrato_id'] in selected_ids]; stages=[r for r in self.stages_cache if r['contrato_id'] in selected_ids]
        contrato_single=self.current_filters['contrato_id'] if self.current_filters['contrato_id'] in selected_ids else (next(iter(selected_ids)) if len(selected_ids)==1 else None)
        curve=list(self.service.dashboard_monthly_curve(contrato_single) or []); heat_level=self.cb_heatmap_mode.currentText().lower(); heat_rows=list(self.service.dashboard_heatmap(contrato_single, heat_level) or [])
        details=list(self.service.dashboard_detail_rows(self.current_filters['contrato_id'] if self.current_filters['contrato_id'] in selected_ids else contrato_single, self.current_filters['etapa_codigo'], self.current_filters['grupo_codigo'], self.current_filters['competencia']) or [])
        previsto=sum(float(r['valor_previsto'] or 0) for r in rows); realizado=sum(float(r['valor_realizado'] or 0) for r in rows); saldo=previsto-realizado
        self.lbl_contratos.setText(f"Contratos\n{len(rows)}"); self.lbl_prev.setText(f"Previsto\n{self._fmt(previsto)}"); self.lbl_real.setText(f"Realizado\n{self._fmt(realizado)}"); self.lbl_saldo.setText(f"Saldo\n{self._fmt(saldo)}"); self.lbl_pend.setText(f"Em aprovação\n{self.aprov_cache.get('em_aprovacao',0)}"); self.lbl_aprov.setText(f"Aprovados\n{self.aprov_cache.get('aprovado',0)}")
        self._plot_curve_s(curve); self._plot_approval(); self._plot_contracts(rows); self._plot_stages(stages, contrato_single); self._plot_heatmap(heat_rows, heat_level); self._fill_detail_table(details)
    def _plot_curve_s(self, rows):
        self.fig1.clear(); ax=self.fig1.add_subplot(111); labels=[r['competencia'] for r in rows]; prev=[float(r['valor_previsto_mes'] or 0) for r in rows]; real=[float(r['valor_realizado_mes'] or 0) for r in rows]; accp=[]; accr=[]; s1=s2=0; self._curve_point_map=[]
        for i,(p,r) in enumerate(zip(prev,real)):
            s1+=p; s2+=r; accp.append(s1); accr.append(s2); self._curve_point_map.append({'idx':i,'competencia':labels[i],'previsto':s1,'realizado':s2,'saldo':s1-s2})
        x=list(range(len(labels))); ax.plot(x, accp, marker='o', linewidth=2, label='Previsto acumulado'); ax.plot(x, accr, marker='o', linewidth=2, label='Realizado acumulado'); ax.fill_between(x, accp, accr, alpha=0.15); ax.set_title('Curva S prevista x realizada'); ax.set_xticks(x); ax.set_xticklabels(labels, rotation=35, ha='right'); ax.grid(True, axis='y', alpha=0.3); ax.legend(); self.fig1.tight_layout(); self.canvas1.draw()
    def _plot_approval(self):
        self.fig2.clear(); ax=self.fig2.add_subplot(111); labels=['Rascunho','Em aprovação','Aprovado','Rejeitado']; vals=[self.aprov_cache.get('rascunho',0), self.aprov_cache.get('em_aprovacao',0), self.aprov_cache.get('aprovado',0), self.aprov_cache.get('rejeitado',0)]; ax.pie(vals, labels=labels, autopct='%1.0f%%'); ax.set_title('Status de aprovação'); self.fig2.tight_layout(); self.canvas2.draw()
    def _plot_contracts(self, rows):
        self.fig3.clear(); ax=self.fig3.add_subplot(111); labels=[r['contrato_codigo'] for r in rows]; prev=[float(r['valor_previsto'] or 0) for r in rows]; real=[float(r['valor_realizado'] or 0) for r in rows]; x=list(range(len(labels))); b1=ax.bar([i-0.2 for i in x], prev, width=0.4, label='Previsto'); b2=ax.bar([i+0.2 for i in x], real, width=0.4, label='Realizado'); self._contract_bar_map=[]
        for i,row in enumerate(rows):
            saldo=prev[i]-real[i]; self._contract_bar_map += [(b1[i], row['contrato_id'], row['contrato_codigo'], {'previsto':prev[i],'realizado':real[i],'saldo':saldo}), (b2[i], row['contrato_id'], row['contrato_codigo'], {'previsto':prev[i],'realizado':real[i],'saldo':saldo})]
        ax.set_title('Previsto x realizado por contrato'); ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha='right'); ax.grid(True, axis='y', alpha=0.3); ax.legend(); self.fig3.tight_layout(); self.canvas3.draw()
    def _plot_stages(self, rows, contrato_single=None):
        self.fig4.clear(); ax=self.fig4.add_subplot(111); rows=[r for r in rows if (not contrato_single or r['contrato_id']==contrato_single)]; rows=sorted(rows, key=lambda r: abs(float(r['valor_previsto'] or 0)-float(r['valor_realizado'] or 0)), reverse=True)[:10]; labels=[f"{r['contrato_codigo']}/{r['etapa_codigo']}" for r in rows]; prev=[float(r['valor_previsto'] or 0) for r in rows]; real=[float(r['valor_realizado'] or 0) for r in rows]; saldo=[p-r for p,r in zip(prev,real)]; y=list(range(len(labels))); self._stage_bar_map=[]
        if self.cb_stage_mode.currentText()=='Saldo':
            bars=ax.barh(y, saldo); [self._stage_bar_map.append((bars[i], rows[i]['etapa_codigo'], {'previsto':prev[i],'realizado':real[i],'saldo':saldo[i]})) for i in range(len(rows))]; ax.set_title('Saldo por etapa')
        else:
            b1=ax.barh([i+0.2 for i in y], prev, height=0.4, label='Previsto'); b2=ax.barh([i-0.2 for i in y], real, height=0.4, label='Realizado'); ax.legend(); ax.set_title('Previsto x realizado por etapa')
            for i,row in enumerate(rows): self._stage_bar_map += [(b1[i], row['etapa_codigo'], {'previsto':prev[i],'realizado':real[i],'saldo':saldo[i]}), (b2[i], row['etapa_codigo'], {'previsto':prev[i],'realizado':real[i],'saldo':saldo[i]})]
        ax.set_yticks(y); ax.set_yticklabels(labels); ax.grid(True, axis='x', alpha=0.3); self.fig4.tight_layout(); self.canvas4.draw()
    def _plot_heatmap(self, rows, level):
        self.fig5.clear(); ax=self.fig5.add_subplot(111)
        if not rows:
            ax.text(0.5,0.5,'Sem dados para heatmap',ha='center',va='center'); ax.set_axis_off(); self.fig5.tight_layout(); self.canvas5.draw(); return
        months=sorted({r['competencia'] for r in rows if r['competencia']}); y_labels=sorted({r['nivel_codigo'] for r in rows if r['nivel_codigo']}); matrix=[]
        for y in y_labels:
            matrix.append([sum(float(r['saldo'] or 0) for r in rows if r['nivel_codigo']==y and r['competencia']==m) for m in months])
        self._heatmap_meta={'xlabels':months,'ylabels':y_labels,'matrix':matrix,'level':level}; img=ax.imshow(matrix, aspect='auto'); ax.set_title(f'Heatmap mensal de desvios por {level}'); ax.set_xticks(range(len(months))); ax.set_xticklabels(months, rotation=35, ha='right'); ax.set_yticks(range(len(y_labels))); ax.set_yticklabels(y_labels); self.fig5.colorbar(img, ax=ax, fraction=0.025, pad=0.02); self.fig5.tight_layout(); self.canvas5.draw()
    def _fill_detail_table(self, rows):
        self.table_dev.setRowCount(0)
        for row in rows:
            r=self.table_dev.rowCount(); self.table_dev.insertRow(r); self.table_dev.setItem(r,0,TextItem(row['contrato_codigo'])); self.table_dev.setItem(r,1,TextItem(row['etapa_codigo'])); self.table_dev.setItem(r,2,TextItem(row['grupo_codigo'])); self.table_dev.setItem(r,3,TextItem(f"{row['entregavel_codigo']} - {row['entregavel_descricao']}")); self.table_dev.setItem(r,4,TextItem(row['competencia'])); self.table_dev.setItem(r,5,CurrencyItem(row['valor_previsto_mes'])); self.table_dev.setItem(r,6,CurrencyItem(row['valor_realizado_mes'])); self.table_dev.setItem(r,7,CurrencyItem(row['saldo']))
    def on_contract_chart_click(self, event):
        if event.inaxes is None: return
        for patch, contrato_id, contrato_codigo, payload in self._contract_bar_map:
            contains,_=patch.contains(event)
            if contains:
                self.current_filters['contrato_id']=contrato_id; self.current_filters['etapa_codigo']=None; self.current_filters['grupo_codigo']=None; self.lbl_hint.setText(f"Contrato {contrato_codigo} | previsto {self._fmt(payload['previsto'])} | realizado {self._fmt(payload['realizado'])} | saldo {self._fmt(payload['saldo'])}. Clique em etapa para continuar o drill-down."); self.refresh_from_selection(); return
    def on_contract_chart_hover(self, event):
        if event.inaxes is None: return
        for patch, _, contrato_codigo, payload in self._contract_bar_map:
            contains,_=patch.contains(event)
            if contains: self.lbl_hint.setText(f"{contrato_codigo} | previsto {self._fmt(payload['previsto'])} | realizado {self._fmt(payload['realizado'])} | saldo {self._fmt(payload['saldo'])}"); return
    def on_curve_click(self, event):
        if event.inaxes is None or event.xdata is None: return
        idx=int(round(event.xdata));
        if idx<0 or idx>=len(self._curve_point_map): return
        point=self._curve_point_map[idx]; self.current_filters['competencia']=point['competencia']; self.lbl_hint.setText(f"Competência {point['competencia']} | previsto acum. {self._fmt(point['previsto'])} | realizado acum. {self._fmt(point['realizado'])} | saldo {self._fmt(point['saldo'])}."); self.refresh_from_selection()
    def on_curve_hover(self, event):
        if event.inaxes is None or event.xdata is None: return
        idx=int(round(event.xdata));
        if idx<0 or idx>=len(self._curve_point_map): return
        p=self._curve_point_map[idx]; self.lbl_hint.setText(f"{p['competencia']} | previsto acum. {self._fmt(p['previsto'])} | realizado acum. {self._fmt(p['realizado'])} | saldo {self._fmt(p['saldo'])}")
    def on_stage_chart_click(self, event):
        if event.inaxes is None: return
        for patch, etapa_codigo, payload in self._stage_bar_map:
            contains,_=patch.contains(event)
            if contains: self.current_filters['etapa_codigo']=etapa_codigo; self.current_filters['grupo_codigo']=None; self.lbl_hint.setText(f"Etapa {etapa_codigo} | previsto {self._fmt(payload['previsto'])} | realizado {self._fmt(payload['realizado'])} | saldo {self._fmt(payload['saldo'])}. Agora o detalhe ficou no nível de entregável."); self.refresh_from_selection(); return
    def on_stage_chart_hover(self, event):
        if event.inaxes is None: return
        for patch, etapa_codigo, payload in self._stage_bar_map:
            contains,_=patch.contains(event)
            if contains: self.lbl_hint.setText(f"Etapa {etapa_codigo} | previsto {self._fmt(payload['previsto'])} | realizado {self._fmt(payload['realizado'])} | saldo {self._fmt(payload['saldo'])}"); return
    def on_heatmap_click(self, event):
        if event.inaxes is None or event.xdata is None or event.ydata is None: return
        x=int(round(event.xdata)); y=int(round(event.ydata)); meta=self._heatmap_meta
        if x<0 or y<0 or x>=len(meta['xlabels']) or y>=len(meta['ylabels']): return
        competencia=meta['xlabels'][x]; nivel_codigo=meta['ylabels'][y]; self.current_filters['competencia']=competencia
        if meta['level']=='etapa': self.current_filters['etapa_codigo']=nivel_codigo
        elif meta['level']=='grupo': self.current_filters['grupo_codigo']=nivel_codigo
        self.lbl_hint.setText(f"Heatmap | {meta['level']}={nivel_codigo} | competência={competencia} | saldo {self._fmt(meta['matrix'][y][x])}."); self.refresh_from_selection()
    def on_heatmap_hover(self, event):
        if event.inaxes is None or event.xdata is None or event.ydata is None: return
        x=int(round(event.xdata)); y=int(round(event.ydata)); meta=self._heatmap_meta
        if x<0 or y<0 or x>=len(meta['xlabels']) or y>=len(meta['ylabels']): return
        self.lbl_hint.setText(f"Heatmap | {meta['level']}={meta['ylabels'][y]} | competência={meta['xlabels'][x]} | saldo {self._fmt(meta['matrix'][y][x])}")
    def export_dashboard_png(self):
        path,_=QFileDialog.getSaveFileName(self,'Salvar dashboard','dashboard.png','PNG (*.png)')
        if not path: return
        if not path.lower().endswith('.png'): path += '.png'
        try: self.grab().save(path); QMessageBox.information(self,'Sucesso',f'Dashboard exportado para:\n{path}')
        except Exception as exc: QMessageBox.warning(self,'Erro',str(exc))
    def export_detail_csv(self):
        path,_=QFileDialog.getSaveFileName(self,'Salvar detalhe','dashboard_detalhe.csv','CSV (*.csv)')
        if not path: return
        if not path.lower().endswith('.csv'): path += '.csv'
        try:
            with open(path,'w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f, delimiter=';'); w.writerow(['Contrato','Etapa','Grupo','Entregável','Competência','Previsto','Realizado','Saldo'])
                for row in range(self.table_dev.rowCount()): w.writerow([self.table_dev.item(row,c).text() if self.table_dev.item(row,c) else '' for c in range(self.table_dev.columnCount())])
            QMessageBox.information(self,'Sucesso',f'Detalhe exportado para:\n{path}')
        except Exception as exc: QMessageBox.warning(self,'Erro',str(exc))
    def marcar_todos(self):
        self.list_contratos.blockSignals(True)
        for i in range(self.list_contratos.count()): self.list_contratos.item(i).setCheckState(Qt.Checked)
        self.list_contratos.blockSignals(False); self.refresh_from_selection()
    def desmarcar_todos(self):
        self.list_contratos.blockSignals(True)
        for i in range(self.list_contratos.count()): self.list_contratos.item(i).setCheckState(Qt.Unchecked)
        self.list_contratos.blockSignals(False); self.refresh_from_selection()
    @staticmethod
    def _fmt(value):
        try: return f"{float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except Exception: return str(value)
