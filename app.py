import streamlit as st
from openfire_sync import executa_lista, retorna_lista
import pandas as pd

st.set_page_config(
    page_title="Coopemg Openfire Sync",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Função para obter a lista de usuários a serem atualizados
def retorna_lista_func():
    openfire, lista_alteracao = retorna_lista()
    st.session_state.lista_alteracao = lista_alteracao
    st.session_state.openfire = openfire

# Função para executar a atualização
def executa_lista_func():
    lista_alteracao = st.session_state.lista_alteracao
    openfire = st.session_state.openfire
    executa_lista(openfire, lista_alteracao)
    st.session_state.execucao = True

# Título da página
st.title("Coopemg Openfire Sync")

# Botões para obter e executar a lista de atualização
st.subheader("Atualização de usuários do Openfire")
st.write("Clique nos botões abaixo para obter e executar a lista de atualização.")

btn_retorna_lista = st.button("Obter lista de atualização", on_click=retorna_lista_func)
btn_executa_lista = st.button("Executar atualização", on_click=executa_lista_func)

# Mensagem de sucesso após a execução
if 'execucao' in st.session_state:
    st.success('Alteração realizada com sucesso!')

# Tabela com a lista de usuários a serem atualizados
if 'lista_alteracao' in st.session_state:
    lista_alteracao = st.session_state.lista_alteracao
    st.subheader(f"Lista de usuários a serem atualizados ({len(lista_alteracao)})")
    table = []
    for line in lista_alteracao:
        usuario = line[0]
        descricao_antiga = line[1]
        descricao_nova = line[2]
        table.append([usuario, descricao_antiga, descricao_nova])
    columns = ["Usuário", "Descrição antiga", "Descrição nova"]
    df = pd.DataFrame(table, columns=columns)
    st.table(df)
