import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from utils.queries import *

st.set_page_config(
  layout = 'wide',
  page_title = 'aaa',
  page_icon='💎',
  initial_sidebar_state="collapsed"
)


# Crie os campos de entrada de data no Streamlit
data_inicio = st.date_input('Data de Início', value=datetime.today()-timedelta(days=1), key='data_inicio_input', format="DD/MM/YYYY")
data_fim = st.date_input('Data de Fim', value=datetime.today(), key='data_fim_input', format="DD/MM/YYYY")

data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)

data_inicio_str = data_inicio.strftime('%Y-%m-%d')
data_fim_str = data_fim.strftime('%Y-%m-%d')

# Construa a URL com as datas variáveis
url_template = "https://eshows.kamino.tech/api/financeiro/movimentoFinanceiro/lista?PeriodoDe={PeriodoDe}&PeriodoAte={PeriodoAte}&IDPlanoContaAtivo=10201"

url = url_template.format(PeriodoDe=data_inicio_str, PeriodoAte=data_fim_str)


# url = "https://eshows.kamino.tech/api/financeiro/movimentoFinanceiro/lista?PeriodoDe=2024-08-01&PeriodoAte=2024-08-14&IDPlanoContaAtivo=10201"

headers = get_headers()

response = requests.get(url, headers=headers)


data = response.json()

df_movimentacao_kamino = pd.DataFrame(data)

df_movimentacao_kamino['Data'] = pd.to_datetime(df_movimentacao_kamino['Data'], format='ISO8601', errors='coerce')

df_movimentacao_kamino['DataPagamento'] = pd.to_datetime(df_movimentacao_kamino['DataPagamento'])


df_movimentacao_kamino_por_data = df_movimentacao_kamino.groupby('DataPagamento')['ValorRealizado'].sum().reset_index()
df_movimentacao_kamino_por_data = df_movimentacao_kamino_por_data.rename(columns={'DataPagamento': 'Data_Pagamento'})

df_movimentacao_kamino.info()

print(response.text)

st.dataframe(df_movimentacao_kamino)

data_corte = '2024-08-01'

df_pagamentos_kamino_epm = GET_PAGAMENTOS_KAMINO(data_corte)
st.dataframe(df_pagamentos_kamino_epm)

df_pagamentos_kamino_epm_por_data = df_pagamentos_kamino_epm.groupby('Data_Pagamento')['Valor'].sum().reset_index()
df_pagamentos_kamino_epm_por_data = df_pagamentos_kamino_epm_por_data.rename(columns={'Valor': 'Valor_EPM'})

df_merged_kamino = pd.merge(df_pagamentos_kamino_epm_por_data, df_movimentacao_kamino_por_data, on = 'Data_Pagamento', how = 'outer')
df_merged_kamino[['Valor_EPM', 'ValorRealizado']] = df_merged_kamino[['Valor_EPM', 'ValorRealizado']].fillna(0)
df_merged_kamino['Valor_EPM'] = df_merged_kamino['Valor_EPM'].astype(float)
df_merged_kamino['ValorRealizado'] = df_merged_kamino['ValorRealizado'].astype(float)

df_merged_kamino['Diferenca_Kamino'] = df_merged_kamino['Valor_EPM'] - df_merged_kamino['ValorRealizado']

df_merged_kamino.info()

df_pagamentos_kamino_epm.info()