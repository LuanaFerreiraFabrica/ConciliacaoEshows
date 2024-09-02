import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from utils.queries import *
from utils.functions.geral import *


st.set_page_config(
  layout = 'wide',
  page_title = 'Conciliação Kamino',
  page_icon='💎',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Inicio.py')

config_sidebar()

col, col2, col3 = st.columns([6, 3, 3])
with col:
  st.title('Conciliação EPM x Kamino')
with col2:
  data_inicio = st.date_input('Data de Início', value=datetime.today()-timedelta(days=1), key='data_inicio_input', format="DD/MM/YYYY")
with col3:
  data_fim = st.date_input('Data de Fim', value=datetime.today(), key='data_fim_input', format="DD/MM/YYYY")
st.markdown('*Se não existem dados a serem mostrados no dia selecionado, o dashboard retorna um erro. Caso isso ocorra, selecione outra data.')

data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)
data_inicio_str = data_inicio.strftime('%Y-%m-%d')
data_fim_str = data_fim.strftime('%Y-%m-%d')

# def config_movimentacao_kamino
url_template = "https://eshows.kamino.tech/api/financeiro/movimentoFinanceiro/lista?PeriodoDe={PeriodoDe}&PeriodoAte={PeriodoAte}&IDPlanoContaAtivo=10201"
url = url_template.format(PeriodoDe=data_inicio_str, PeriodoAte=data_fim_str)
headers = get_headers()
response = requests.get(url, headers=headers)
dfMovimentacaoKamino = pd.DataFrame(response.json())
dfMovimentacaoKamino['DataPagamento'] = pd.to_datetime(dfMovimentacaoKamino['DataPagamento'])
dfMovimentacaoKaminoGrouped = dfMovimentacaoKamino.groupby('DataPagamento')['ValorRealizado'].sum().reset_index()
columnsDfMovimentacaoKamino = ['ID', 'DataPagamento', 'ValorRealizado', 'IDContaOrigem', 'NomeContaOrigem', 'IDContaDestino', 'NomeContaDestino', 'IDPessoa', 'NomePessoa', 'Descricao']
dfMovimentacaoKamino = dfMovimentacaoKamino[columnsDfMovimentacaoKamino]


dfMovimentacaoKaminoGrouped = dfMovimentacaoKaminoGrouped.rename(columns={'DataPagamento': 'Data_Pagamento', 'ValorRealizado': 'Valor_Realizado_Kamino'})

dfPagamentosKaminoEpm = GET_PAGAMENTOS_KAMINO(data_inicio, data_fim)

# def config_conciliacao_epm_kamino(dfepm)
dfPagamentosKaminoEpmGrouped = dfPagamentosKaminoEpm.groupby('Data_Pagamento')['Valor'].sum().reset_index()
dfPagamentosKaminoEpmGrouped = dfPagamentosKaminoEpmGrouped.rename(columns={'Valor': 'Valor_Realizado_EPM'})
dfMergedKamino = pd.merge(dfPagamentosKaminoEpmGrouped, dfMovimentacaoKaminoGrouped, on = 'Data_Pagamento', how = 'outer')
dfMergedKamino[['Valor_Realizado_EPM', 'Valor_Realizado_Kamino']] = dfMergedKamino[['Valor_Realizado_EPM', 'Valor_Realizado_Kamino']].fillna(0)
dfMergedKamino['Valor_Realizado_EPM'] = dfMergedKamino['Valor_Realizado_EPM'].astype(float)
dfMergedKamino['Valor_Realizado_Kamino'] = dfMergedKamino['Valor_Realizado_Kamino'].astype(float)
dfMergedKamino['Diferença'] = dfMergedKamino['Valor_Realizado_EPM'] - dfMergedKamino['Valor_Realizado_Kamino']



dfMovimentacaoKamino = format_columns_brazilian(dfMovimentacaoKamino, ['ValorRealizado'])
dfPagamentosKaminoEpm = format_columns_brazilian(dfPagamentosKaminoEpm, ['Valor'])
dfMergedKamino = format_columns_brazilian(dfMergedKamino, ['Valor_Realizado_EPM', 'Valor_Realizado_Kamino', 'Diferença'])



with st.container(border=True):
  st.subheader('Diferença EPM vs Kamino')
  st.dataframe(dfMergedKamino, hide_index=True)
with st.container(border=True):
  st.subheader('Movimentação Kamino')
  st.dataframe(dfMovimentacaoKamino, hide_index=True)
with st.container(border=True):
  st.subheader('Movimentação EPM')
  st.dataframe(dfPagamentosKaminoEpm, hide_index=True)


