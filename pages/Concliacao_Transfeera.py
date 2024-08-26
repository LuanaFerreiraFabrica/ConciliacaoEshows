import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from utils.queries import *
from utils.functions.geral import *


st.set_page_config(
  layout = 'wide',
  page_title = 'Conciliação Transfeera',
  page_icon='💎',
  initial_sidebar_state="collapsed"
)
config_sidebar()


col, col2, col3 = st.columns([6, 3, 3])
with col:
  st.title('Conciliação EPM x Transfeera')
with col2:
  data_inicio = st.date_input('Data de Início', value=datetime.today()-timedelta(days=1), key='data_inicio_input', format="DD/MM/YYYY")
with col3:
  data_fim = st.date_input('Data de Fim', value=datetime.today(), key='data_fim_input', format="DD/MM/YYYY")

data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)

data_inicio_str = data_inicio.strftime('%Y-%m-%d')
data_fim_str = data_fim.strftime('%Y-%m-%d')




extrato_transfeera= GET_EXTRATO_TRANSFEERA(data_inicio, data_fim)
pagamentos_propostas = GET_PAGAMENTOS_PROPOSTAS(data_inicio, data_fim)

extrato_transfeera = extrato_transfeera.drop_duplicates(subset='ID_Transacao_Transfeera', keep='first')

extratoTransfeeraGrouped = extrato_transfeera.groupby('Data_Pagamento')['Valor_Pagamento_Transfeera'].sum().reset_index()
pagamentosPropostasGrouped = pagamentos_propostas.groupby('Data_Pagamento')['Valor_Pagamento_Proposta'].sum().reset_index()


dfMergedTransfeera = pd.merge(extratoTransfeeraGrouped, pagamentosPropostasGrouped, on = 'Data_Pagamento', how = 'outer')
dfMergedTransfeera[['Valor_Pagamento_Transfeera', 'Valor_Pagamento_Proposta']] = dfMergedTransfeera[['Valor_Pagamento_Transfeera', 'Valor_Pagamento_Proposta']].fillna(0)
dfMergedTransfeera['Valor_Pagamento_Proposta'] = dfMergedTransfeera['Valor_Pagamento_Proposta'].astype(float)
dfMergedTransfeera['Valor_Pagamento_Transfeera'] = dfMergedTransfeera['Valor_Pagamento_Transfeera'].astype(float)
dfMergedTransfeera['Diferença'] = dfMergedTransfeera['Valor_Pagamento_Proposta'] - dfMergedTransfeera['Valor_Pagamento_Transfeera']



extrato_transfeera = format_columns_brazilian(extrato_transfeera, ['Valor_Pagamento_Transfeera'])
pagamentos_propostas = format_columns_brazilian(pagamentos_propostas, ['Valor_Pagamento_Proposta'])
dfMergedTransfeera = format_columns_brazilian(dfMergedTransfeera, ['Valor_Pagamento_Transfeera', 'Valor_Pagamento_Proposta', 'Diferença'])


with st.container(border=True):
  st.subheader('Diferença EPM vs Transfeera')
  st.dataframe(dfMergedTransfeera, hide_index=True)
with st.container(border=True):
  st.subheader('Extrato Transfeera')
  st.dataframe(extrato_transfeera, hide_index=True)
with st.container(border=True):
  st.subheader('Pagamentos nas Propostas')
  st.dataframe(pagamentos_propostas, hide_index=True)