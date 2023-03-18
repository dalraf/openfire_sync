import streamlit as st
from openfire_sync import executa_lista, retorna_lista

st.set_page_config(
    page_title="Coopemg Openfire Sync",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("### Atualização de usuários do Openfire")


def retorna_lista_func():
    openfire, lista_alteracao = retorna_lista()
    st.session_state.lista_alteracao = lista_alteracao
    st.session_state.openfire = openfire

def executa_lista_func():
    lista_alteracao = st.session_state.lista_alteracao
    openfire = st.session_state.openfire
    executa_lista(openfire, lista_alteracao)
    st.session_state.execucao = True



st.button("Pegar lista de atualização", on_click=retorna_lista_func)
if 'lista_alteracao' in st.session_state:
    st.button("Executar atualização", on_click=executa_lista_func)

if 'execucao' in st.session_state:
    st.markdown('---')
    st.markdown('Alteração realizada com sucesso!')


if 'lista_alteracao' in st.session_state:
    lista_alteracao = st.session_state.lista_alteracao
    st.markdown('---')
    st.markdown(f'##### Numero de usuários a serem atualizados: {len(lista_alteracao)} ')
    for line in lista_alteracao:
        usuario = line[0]
        descricao_antiga = line[1]
        descricao_nova = line[2]
        st.markdown('---')
        st.markdown(f'Usuário: {usuario}')
        st.markdown(f'Descrição antiga: *{descricao_antiga}*')
        st.markdown(f'Descrição nova: *{descricao_nova}*')



    
