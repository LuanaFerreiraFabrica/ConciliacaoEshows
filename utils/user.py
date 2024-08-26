import streamlit as st


def login(userName: str, password: str) -> bool:
  # Carregar username e password do st.secrets
  USERNAME = st.secrets["credentials"]["user"]
  PASSWORD = st.secrets["credentials"]["password2"]
  # Verifica se o usuário e senha fornecidos correspondem aos armazenados no st.secrets
  if userName == USERNAME and password == PASSWORD:
    return True
  else:
    return False

def logout():
    st.session_state['loggedIn'] = False
    st.switch_page('Login.py')

def handle_login(userName, password):
    if login(userName, password):
        st.session_state['loggedIn'] = True
        st.session_state['userName'] = userName 
    else:
        st.session_state['loggedIn'] = False
        st.error("Email ou senha inválidos!!")
