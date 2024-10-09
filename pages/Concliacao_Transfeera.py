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

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Inicio.py')

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


estornos = GET_ESTORNOS(data_inicio, data_fim)
problemasOperacionais = GET_PROBLEMAS_OPERACIONAIS(data_inicio, data_fim)

estornosGrouped = estornos.groupby('Data_Pagamento')['Valor_Estornos'].sum().reset_index()
problemasOperacionaisGrouped = problemasOperacionais.groupby('Data_Pagamento')['Valor_Problemas_Operacionais'].sum().reset_index()

def config_merged_transfeera(df1, df2):
  dfMergedTransfeera = pd.merge(df1, df2, on = 'Data_Pagamento', how = 'outer')
  dfMergedTransfeera[['Valor_Pagamento_Transfeera', 'Valor_Pagamento_Proposta']] = dfMergedTransfeera[['Valor_Pagamento_Transfeera', 'Valor_Pagamento_Proposta']].fillna(0)
  dfMergedTransfeera['Valor_Pagamento_Proposta'] = dfMergedTransfeera['Valor_Pagamento_Proposta'].astype(float)
  dfMergedTransfeera['Valor_Pagamento_Transfeera'] = dfMergedTransfeera['Valor_Pagamento_Transfeera'].astype(float)
  dfMergedTransfeera['Diferença Inicial'] = dfMergedTransfeera['Valor_Pagamento_Proposta'] - dfMergedTransfeera['Valor_Pagamento_Transfeera']
  return dfMergedTransfeera

dfMergedTransfeera = config_merged_transfeera(extratoTransfeeraGrouped, pagamentosPropostasGrouped)
dfMergedEstornosPO = pd.merge(estornosGrouped, problemasOperacionaisGrouped, on = 'Data_Pagamento', how = 'outer')
dfMergedFinal = pd.merge(dfMergedTransfeera, dfMergedEstornosPO, on = 'Data_Pagamento', how = 'outer')

dfMergedFinal[['Valor_Estornos', 'Valor_Problemas_Operacionais']] = dfMergedFinal[['Valor_Estornos', 'Valor_Problemas_Operacionais']].fillna(0)
dfMergedFinal['Valor_Estornos'] = dfMergedFinal['Valor_Estornos'].astype(float)
dfMergedFinal['Valor_Problemas_Operacionais'] = dfMergedFinal['Valor_Problemas_Operacionais'].astype(float)
dfMergedFinal['Diferença Final'] = dfMergedFinal['Diferença Inicial'] + dfMergedFinal['Valor_Estornos'] + dfMergedFinal['Valor_Problemas_Operacionais']



pagamentos_propostas_grouped = pagamentos_propostas.groupby(['Data_Pagamento', 'Conta_Beneficiado'], as_index=False).agg({
  'Valor_Pagamento_Proposta': 'sum',
})
diferencas_valores = pd.merge(extrato_transfeera, pagamentos_propostas_grouped, on = ['Data_Pagamento', 'Conta_Beneficiado'], how = 'outer')

diferencas_valores = diferencas_valores[diferencas_valores.isnull().any(axis=1)]

extrato_transfeera = format_columns_brazilian(extrato_transfeera, ['Valor_Pagamento_Transfeera'])
pagamentos_propostas = format_columns_brazilian(pagamentos_propostas, ['Valor_Pagamento_Proposta'])
dfMergedFinal = format_columns_brazilian(dfMergedFinal, ['Valor_Pagamento_Transfeera', 'Valor_Pagamento_Proposta', 'Diferença Inicial', 
                                                         'Valor_Estornos', 'Valor_Problemas_Operacionais', 'Diferença Final'])
diferencas_valores = format_columns_brazilian(diferencas_valores, ['Valor_Pagamento_Proposta'])



extrato_transfeera = format_date_brazilian(extrato_transfeera, 'Data_Pagamento')
pagamentos_propostas = format_date_brazilian(pagamentos_propostas, 'Data_Pagamento')
dfMergedFinal = format_date_brazilian(dfMergedFinal, 'Data_Pagamento')
diferencas_valores = format_date_brazilian(diferencas_valores, 'Data_Pagamento')



with st.container(border=True):
  st.subheader('Conciliação EPM, Transfeera, Estornos e Problemas Operacionais')
  st.dataframe(dfMergedFinal, hide_index=True)
with st.container(border=True):
  st.subheader('Diferenças Detalhadas')
  st.dataframe(diferencas_valores, hide_index=True)
with st.container(border=True):
  st.subheader('Estornos')
  st.dataframe(estornos, hide_index=True)
with st.container(border=True):
  st.subheader('Problemas Operacionais')
  st.dataframe(problemasOperacionais, hide_index=True)
with st.container(border=True):
  st.subheader('Extrato Transfeera')
  st.dataframe(extrato_transfeera, hide_index=True)
with st.container(border=True):
  st.subheader('Pagamentos nas Propostas')
  st.dataframe(pagamentos_propostas, hide_index=True)
