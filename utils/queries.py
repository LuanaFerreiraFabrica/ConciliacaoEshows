import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import mysql.connector

LOGGER = get_logger(__name__)

def mysql_connection(connection_name):
  mysql_config = st.secrets[connection_name]
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

def execute_query(query, connection_name):
  conn = mysql_connection(connection_name)
  cursor = conn.cursor()
  cursor.execute(query)

  # Obter nomes das colunas
  column_names = [col[0] for col in cursor.description]
  
  # Obter resultados
  result = cursor.fetchall()
  
  cursor.close()
  return result, column_names


def dataframe_query(connection_name, query):
  resultado, nomeColunas = execute_query(query, connection_name)
  dataframe = pd.DataFrame(resultado, columns=nomeColunas)
  return dataframe


def GET_PAGAMENTOS_KAMINO(data_inicio, data_fim):
   return dataframe_query("grupoe", f'''
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
      AND tcie.DATA_PAGAMENTO >= '{data_inicio}'
      AND tcie.DATA_PAGAMENTO <= '{data_fim}'
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
      AND tcce.DATA_PAGAMENTO >= '{data_inicio}'
      AND tcce.DATA_PAGAMENTO <= '{data_fim}'
    ''') 



def GET_EXTRATO_TRANSFEERA(data_inicio, data_fim):
  return dataframe_query("eshows", f'''
  SELECT 
  	tcp.ID AS ID_Cociliação,
  	tcp.DATA_PAGAMENTO AS Data_Pagamento,
  	tcp.ID_TRANSACAO AS ID_Transacao_Transfeera,
  	tcp.VALOR_PAGAMENTO AS Valor_Pagamento_Transfeera,
  	tcp.ID_INTEGRACAO AS Beneficiado,
  	tcp.CONTA AS Conta_beneficiado
  FROM T_CONCILIACAO_PAGAMENTOS tcp
  WHERE tcp.DATA_PAGAMENTO >= '{data_inicio}'
    AND tcp.DATA_PAGAMENTO <= '{data_fim}'
''')


def GET_PAGAMENTOS_PROPOSTAS(data_inicio, data_fim):
  return dataframe_query("eshows", f'''
  SELECT 
	  tp.ID AS ID_Proposta,
  	tp.DATA_PAGAMENTO AS Data_Pagamento,
  	tp.VALOR_ARTISTA_RECEBIMENTO AS Valor_Pagamento_Proposta,
  	tab.NOME_TITULAR AS Beneficiado,
  	tab.NUMERO_CONTA AS Conta_Beneficiado
  FROM T_PROPOSTAS tp
  LEFT JOIN T_ATRACAO_BANCOS tab ON tp.FK_ATRACAO_BANCO  = tab.ID 
  WHERE tp.DATA_PAGAMENTO IS NOT NULL
    AND tp.DATA_PAGAMENTO >= '{data_inicio}'
    AND tp.DATA_PAGAMENTO <= '{data_fim}'
''')