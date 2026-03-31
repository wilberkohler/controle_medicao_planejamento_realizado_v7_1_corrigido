# Controle de Medição - Planejamento x Realizado v2

Projeto desktop em Python com:
- PySide6
- SQLite
- CRUDs completos
- filtros por texto e combos
- planejamento versionado
- realizado mensal
- comparativos
- dashboard com gráficos

## Instalação
```bash
python -m pip install -r requirements.txt
```

## Execução
```bash
python main.py
```

## Módulos
- Dashboard
- Contratos
- Medições
- Etapas
- Grupos
- Entregáveis
- Planejamento (Versões)
- Planejamento Itens
- Planejamento Mensal
- Realizado Mensal
- Comparativo Mensal
- Comparativo Acumulado


## Melhorias desta versão
- calendário visual disponível para integração nas próximas telas de data
- máscaras brasileiras inteligentes para moeda e percentual
- cores para status e saldos
- tela única em árvore para a estrutura do contrato
- comparativo acumulado implementado

## Prioridades 1 a 3 implementadas nesta versão
- calendário visual conectado às principais telas com campos de data
- máscaras brasileiras melhores para moeda e percentual
- combos pesquisáveis
- menu lateral para navegação principal
- filtros avançados por combos nas telas principais
- curva S prevista x realizada no dashboard
- drill-down a partir da árvore estrutural
- coloração visual de status e saldos


## v4.2 - próximo ciclo
- histórico automático em contratos, medições, etapas, grupos, entregáveis e planejamento
- usuários e seleção de usuário ativo
- permissões por perfil
- workflow e histórico integrados
- indicadores de aprovação no dashboard


## v4.3 - próximo passo
- usuário ativo passa a ser registrado no histórico e workflow
- permissões por perfil aplicadas no menu principal
- histórico automático consolidado nos módulos principais
- dashboard com indicadores de aprovação
- base pronta para travas de workflow por módulo de forma mais rígida


## v4.4 - dashboard refinado
- exportação do dashboard em PNG
- exportação de desvios em CSV
- heatmap mensal de desvios
- clique no gráfico por contrato para filtro rápido
- hover com leitura rápida no gráfico por contrato

- heatmap com alternância entre contrato, etapa e grupo


## v4.6 - login inicial
- tela inicial de login
- título institucional do sistema
- identidade visual NAEST em formato textual/estilizado no app
- seleção de usuário via tela de acesso


## v4.7 - produtividade econômico-financeira
- módulo baseado na planilha enviada
- separação entre Previsto, Receita Faturada e Custos
- parâmetros por disciplina: horas por A1 e custo hora equipe
- metas mensais por projetista/contrato
- realizado de produtividade com A1 produzido e receita faturada
- custos de equipe, consultores e terceiros
- dashboard integrando meta, produção, receita, custos, margem e produtividade


## v4.8 - produtividade econômico-financeira ampliada
- apropriação automática de custo de equipe via horas da equipe × custo-hora da disciplina
- margem consolidada por contrato, etapa e grupo
- ranking de projetistas com custo e margem de equipe
- maiores desvios de receita e margem por estrutura
- cards executivos integrando receita e margem da produtividade ao dashboard principal


## v4.9 - DRE gerencial por contrato
- DRE gerencial por contrato
- imposto parametrizado sobre a margem
- padrão inicial de 16,8%
- margem bruta, impostos e margem líquida por contrato
- exportação do DRE em CSV


## v5.0 - DRE por contrato, etapa e grupo
- DRE com alternância entre contrato, etapa e grupo
- filtro opcional por contrato para detalhar etapa/grupo
- mesma regra de imposto sobre a margem
- gráficos e exportação CSV no nível selecionado


## v5.1 - correção da base de imposto no DRE
- imposto passa a incidir sobre o faturamento
- o efeito do imposto passa a refletir na margem líquida
- ajuste aplicado ao DRE por contrato, etapa e grupo


## v5.2 - DRE mais gerencial
- separação entre receita bruta, deduções/impostos e receita líquida
- margem operacional no lugar de foco apenas em margem líquida
- gráficos com estrutura de receita e margem operacional


## v5.3 - exportação e despesas gerais
- centro de exportação para apoio contábil/gerencial
- despesas gerais previstas e realizadas
- categorias como viagens, combustíveis, hospedagem, alimentação, software, plotagem e outras
- inclusão dessas despesas no ecossistema de gestão e nas exportações


## v5.4 - DRE com despesas gerais integradas
- despesas gerais realizadas passam a compor o custo total do DRE
- DRE exibe explicitamente despesas gerais além de custo equipe e custo terceiros
- centro de exportação mostra total de despesas/custos por contrato


## v5.5 - visão mensal por competência
- DRE com visão mensal por competência
- manutenção da visão estrutural por contrato/etapa/grupo
- visão importante para contador e planejamento anual
- exportação CSV também na visão mensal


## v5.6 - exportação anual consolidada
- exportação anual por contrato
- exportação anual mensal por competência
- exportação anual por categoria de despesas
- painel visual para apoio ao contador e ao planejamento anual
\n\n## v5.8 - exportação Excel única\n- exportação única em Excel com múltiplas abas\n- abas para contratos, mensal e categorias de despesas\n- formato mais prático para contador e diretoria\n


## v6.1 - usabilidade e operação
- central de trabalho com pendências, competências, desvios, últimos lançamentos e atalhos
- menu agrupado por blocos funcionais
- campo de busca global por contrato, projetista, competência, categoria e entregável
- lançamentos em grade para despesas realizadas
- estados visuais mais claros em home e aprovações


## v6.4 - importação financeira híbrida
- planilha padrão oficial para entrada financeira
- importação híbrida: planilha valida/importa e o sistema oficializa
- validação de contratos, competência, categorias e valores
- armazenamento oficial de orçamento inicial, revisão orçamentária e faturamento mensal
- despesas previstas/realizadas também podem ser importadas em lote
