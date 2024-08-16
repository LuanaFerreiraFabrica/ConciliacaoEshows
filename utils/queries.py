import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import mysql.connector

LOGGER = get_logger(__name__)

def mysql_connection():
  mysql_config = st.secrets["mysql"]
  # Cria a conexão com MySQL
  conn = mysql.connector.connect(
    host=mysql_config['host'],
    port=mysql_config['port'],
    database=mysql_config['database'],
    user=mysql_config['username'],
    password=mysql_config['password']
  )    
  return conn

def get_headers():
  headers_config = st.secrets["headers"]
  headers = {
    "accept": headers_config['accept'],
    "CN": headers_config['CN'],
    "App": headers_config['App'],
    "IDUsr": headers_config['IDUsr'],
    "Hash": headers_config['Hash'],
    "Usr": headers_config['Usr']
  }  
  return headers

def execute_query(query):
  conn = mysql_connection()
  cursor = conn.cursor()
  cursor.execute(query)

  # Obter nomes das colunas
  column_names = [col[0] for col in cursor.description]
  
  # Obter resultados
  result = cursor.fetchall()
  
  cursor.close()
  return result, column_names


def dataframe_query(query):
  resultado, nomeColunas = execute_query(query)
  dataframe = pd.DataFrame(resultado, columns=nomeColunas)
  return dataframe


def GET_PAGAMENTOS_KAMINO(data_corte):
   return dataframe_query(f'''
    SELECT
    tcie.ID as 'ID',
    tcie.DATA_PAGAMENTO as 'Data_Pagamento',
    tcp.DESCRICAO as 'Classificacao',
    tcie.DESCRICAO as 'Descricao_Custo',
    tcie.VALOR as 'Valor'
    FROM T_CUSTOS_INTERNOS_ESHOWS tcie 
    INNER JOIN T_CLASSIFICACAO_PRIMARIA tcp ON (tcie.FK_CLASSIFICACAO_PRIMARIA = tcp.ID)
    LEFT JOIN T_CONTAS_BANCARIAS tcb ON (tcie.FK_CONTA_BANCARIA = tcb.ID)
    WHERE tcb.ID = 102
    AND tcie.DATA_PAGAMENTO >= '{data_corte}'
    UNION ALL
    SELECT 
    tcce.ID as 'ID',
    tcce.DATA_PAGAMENTO as 'Data_Pagamento',
    tcp.DESCRICAO as 'Classificacao',
    tce.NOME as 'Descricao_Custo',
    tcce.VALOR as 'Valor'
    FROM T_CUSTOS_COLABORADORES_ESHOWS tcce
    LEFT JOIN T_COLABORADORES_ESHOWS tce ON (tcce.FK_COLABORADOR = tce.ID)
    LEFT JOIN T_CLASSIFICACAO_PRIMARIA tcp ON (tcce.FK_CLASSIFICACAO_PRIMARIA = tcp.ID)
    LEFT JOIN T_CONTAS_BANCARIAS tcb ON (tcce.FK_CONTA_BANCARIA = tcb.ID)
    WHERE tcb.ID = 102
    AND tcce.DATA_PAGAMENTO >= '{data_corte}'
    ''') 