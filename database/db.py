import sqlite3
from config.settings import DB_DIR, DB_PATH

def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        '''
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            cliente TEXT,
            data_inicio TEXT,
            data_fim TEXT,
            valor_total_contrato REAL DEFAULT 0,
            percentual_sinal REAL DEFAULT 0,
            status TEXT DEFAULT 'planejamento',
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS medicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            numero_medicao INTEGER NOT NULL,
            competencia TEXT NOT NULL,
            data_inicio_periodo TEXT,
            data_fim_periodo TEXT,
            status TEXT DEFAULT 'aberta',
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            UNIQUE (contrato_id, numero_medicao)
        );

        CREATE TABLE IF NOT EXISTS etapas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            ordem INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            UNIQUE (contrato_id, codigo)
        );

        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            ordem INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
            UNIQUE (etapa_id, codigo)
        );

        CREATE TABLE IF NOT EXISTS entregaveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            unidade TEXT,
            ordem INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
            UNIQUE (grupo_id, codigo)
        );

        CREATE TABLE IF NOT EXISTS planejamento_cabecalho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            versao INTEGER NOT NULL,
            descricao_versao TEXT,
            data_base TEXT,
            status TEXT DEFAULT 'rascunho',
            motivo_revisao TEXT,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            UNIQUE (contrato_id, versao)
        );

        CREATE TABLE IF NOT EXISTS planejamento_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planejamento_id INTEGER NOT NULL,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            entregavel_id INTEGER NOT NULL,
            valor_previsto_total REAL DEFAULT 0,
            percentual_previsto_total REAL DEFAULT 0,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (planejamento_id) REFERENCES planejamento_cabecalho(id) ON DELETE CASCADE,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
            FOREIGN KEY (entregavel_id) REFERENCES entregaveis(id) ON DELETE CASCADE,
            UNIQUE (planejamento_id, entregavel_id)
        );

        CREATE TABLE IF NOT EXISTS planejamento_mensal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planejamento_item_id INTEGER NOT NULL,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            entregavel_id INTEGER NOT NULL,
            competencia TEXT NOT NULL,
            valor_previsto_mes REAL DEFAULT 0,
            percentual_previsto_mes REAL DEFAULT 0,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (planejamento_item_id) REFERENCES planejamento_itens(id) ON DELETE CASCADE,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
            FOREIGN KEY (entregavel_id) REFERENCES entregaveis(id) ON DELETE CASCADE,
            UNIQUE (planejamento_item_id, competencia)
        );

        CREATE TABLE IF NOT EXISTS realizado_mensal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            medicao_id INTEGER NOT NULL,
            etapa_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            entregavel_id INTEGER NOT NULL,
            competencia TEXT NOT NULL,
            valor_realizado_mes REAL DEFAULT 0,
            percentual_realizado_mes REAL DEFAULT 0,
            data_lancamento TEXT,
            responsavel TEXT,
            fonte TEXT DEFAULT 'manual',
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (medicao_id) REFERENCES medicoes(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
            FOREIGN KEY (entregavel_id) REFERENCES entregaveis(id) ON DELETE CASCADE,
            UNIQUE (medicao_id, entregavel_id)
        );


        CREATE TABLE IF NOT EXISTS produtividade_parametros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disciplina TEXT NOT NULL UNIQUE,
            horas_por_a1 REAL DEFAULT 0,
            custo_hora_equipe REAL DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS produtividade_metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER,
            grupo_id INTEGER,
            competencia TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            meta_mensal_a1 REAL DEFAULT 0,
            horas_por_a1 REAL DEFAULT 0,
            horas_planejadas REAL DEFAULT 0,
            receita_prevista REAL DEFAULT 0,
            observacoes TEXT,
            status TEXT DEFAULT 'planejado',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE SET NULL,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS produtividade_realizado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER,
            grupo_id INTEGER,
            entregavel_id INTEGER,
            competencia TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            produzido_a1 REAL DEFAULT 0,
            horas_por_a1 REAL DEFAULT 0,
            horas_equipe REAL DEFAULT 0,
            receita_faturada REAL DEFAULT 0,
            observacoes TEXT,
            status_aprovacao TEXT DEFAULT 'rascunho',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE SET NULL,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE SET NULL,
            FOREIGN KEY (entregavel_id) REFERENCES entregaveis(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS produtividade_custos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            contrato_id INTEGER NOT NULL,
            etapa_id INTEGER,
            grupo_id INTEGER,
            competencia TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            tipo_recurso TEXT NOT NULL,
            fornecedor_nome TEXT,
            horas REAL DEFAULT 0,
            custo_hora REAL DEFAULT 0,
            custo_total REAL DEFAULT 0,
            observacoes TEXT,
            status_aprovacao TEXT DEFAULT 'rascunho',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE,
            FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE SET NULL,
            FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            perfil TEXT NOT NULL DEFAULT 'consulta',
            ativo INTEGER NOT NULL DEFAULT 1,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS historico_alteracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela TEXT NOT NULL,
            registro_id INTEGER NOT NULL,
            acao TEXT NOT NULL,
            usuario_id INTEGER,
            resumo TEXT,
            workflow_status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS workflow_aprovacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modulo TEXT NOT NULL,
            registro_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'rascunho',
            usuario_solicitante_id INTEGER,
            usuario_aprovador_id INTEGER,
            data_solicitacao TEXT,
            data_aprovacao TEXT,
            comentario TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_solicitante_id) REFERENCES usuarios(id) ON DELETE SET NULL,
            FOREIGN KEY (usuario_aprovador_id) REFERENCES usuarios(id) ON DELETE SET NULL
        );



        CREATE TABLE IF NOT EXISTS despesas_planejamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER,
            competencia TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            fornecedor TEXT,
            valor_previsto REAL NOT NULL DEFAULT 0,
            centro_custo TEXT,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS despesas_realizado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER,
            competencia TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            fornecedor TEXT,
            valor_realizado REAL NOT NULL DEFAULT 0,
            documento_ref TEXT,
            centro_custo TEXT,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE SET NULL
        );


        CREATE TABLE IF NOT EXISTS financeiro_orcamento_oficial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            competencia TEXT NOT NULL,
            versao INTEGER NOT NULL DEFAULT 1,
            tipo_orcamento TEXT NOT NULL DEFAULT 'inicial',
            valor_receita REAL NOT NULL DEFAULT 0,
            centro_custo TEXT,
            observacoes TEXT,
            fonte TEXT DEFAULT 'importacao_planilha',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS financeiro_faturamento_oficial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER NOT NULL,
            competencia TEXT NOT NULL,
            documento_ref TEXT,
            valor_faturado REAL NOT NULL DEFAULT 0,
            impostos_percentual REAL DEFAULT 16.8,
            observacoes TEXT,
            fonte TEXT DEFAULT 'importacao_planilha',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS importacoes_financeiras_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo_nome TEXT NOT NULL,
            status TEXT NOT NULL,
            resumo TEXT,
            detalhes_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS dre_parametros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imposto_percentual REAL NOT NULL DEFAULT 16.8,
            ativo INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        '''
    )
    conn.commit()
    conn.close()
