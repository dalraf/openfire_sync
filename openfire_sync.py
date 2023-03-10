import requests
from io import BytesIO
import pandas as pd
from openfire import Openfire
import jellyfish
from pprint import pprint
from time import sleep
from sys import argv
from config import (
    planilha_url,
    openfire_password,
    cooperativa_code,
    openfire_api,
    openfire_user,
)


def get_file_data(url):
    response = requests.get(url)
    f = BytesIO()
    for chunk in response.iter_content(chunk_size=1024):
        f.write(chunk)
    f.seek(0)
    return f

def get_openfire_object():
    openfire = Openfire(openfire_user, openfire_password, cooperativa_code, openfire_api)
    openfire.get_all_users()
    return openfire

def get_planilha_coopemg():
    coopemg_arquivo_data = get_file_data(planilha_url)
    planilha_coopemg = pd.read_excel(
        coopemg_arquivo_data, skiprows=6, index_col=None, header=None
    )

    planilha_coopemg[1] = planilha_coopemg[1].fillna(method="ffill")
    planilha_coopemg.dropna(thresh=5, axis=0, inplace=True)
    planilha_coopemg.fillna("", inplace=True)
    return planilha_coopemg


def get_users_for_update():
    planilha_coopemg = get_planilha_coopemg()
    lista_users_for_update = []
    for j in planilha_coopemg.iterrows():
        try:
            nome = j[1][2].strip()
            if nome != "":
                cargo = j[1][1].strip()
                ramal = j[1][4] if j[1][3] != "*" else ""
                telefone = (
                    j[1][3] if "Apenas Ramal" not in j[1][2] and "*" not in j[1][2] else ""
                )
                celular = j[1][5] if j[1][4] != "*" else ""
                lista_users_for_update.append([nome, cargo, ramal, telefone, celular])
        except Exception as e:
            print(j)
            print(e.args[0])
            exit(1)
    return lista_users_for_update

def get_lista_usuario_match_for_update(openfire):
    lista_users_for_update = get_users_for_update()
    lista_usuario_match_for_update = []
    for row in lista_users_for_update:
        nome_search = str(row[0])
        if not any([i in nome_search for i in ["Sem Atendente", "*"]]):
            setor = " - " + str(row[1]) if str(row[1]) != "" else " - Sem Setor"
            ramal_interno = (
                " - " + str(row[2]).strip()
                if str(row[2]).strip() != "" and str(row[2]).strip() != "*"
                else ""
            )
            telefone_fixo = (
                " - " + str(row[3]).strip()
                if str(row[3]).strip() != "" and str(row[3]).strip() != "*"
                else ""
            )
            celular = (
                " / " + str(row[4]).strip()
                if str(row[4]).strip() != "" and str(row[4]).strip() != "*"
                else ""
            )
            contato = ramal_interno + telefone_fixo + celular
            semelhanca_maior = 0
            for user in openfire.users_list:
                nome_real = user[1].strip().replace("???", "-").split("-")[0].strip()
                semelhanca = jellyfish.jaro_similarity(nome_search, nome_real)
                if semelhanca > semelhanca_maior:
                    nome_certo = nome_search
                    id = user[0]
                    semelhanca_maior = semelhanca
                    descricao_antiga = user[1]
            if semelhanca_maior > 0.9:
                descricao_nova = nome_certo + setor + contato
                if descricao_nova != descricao_antiga:
                    lista_usuario_match_for_update.append(
                        [id, descricao_antiga, descricao_nova]
                    )
    return lista_usuario_match_for_update


def run_update(openfire, lista_usuario_match_for_update):
    for user in lista_usuario_match_for_update:
        print("Alterando usu??rio: ", user[0])
        print("Descri????o antiga: ", user[1])
        print("Descri????o nova: ", user[2])
        retorno = openfire.update_user_name(user[0], user[2])
        print(user[0], retorno)


def main(automatico=False):
    if automatico:
        while True:
            openfire = get_openfire_object()
            lista_usuario_match_for_update = get_lista_usuario_match_for_update(openfire)
            if len(lista_usuario_match_for_update) == 0:
                print("N??o h?? usu??rios a serem alterados.")
            else:
                print('Executando essas altera????es:')
                print(lista_usuario_match_for_update)
                run_update(openfire, lista_usuario_match_for_update)
            sleep(60)
    else:
        openfire = get_openfire_object()
        lista_usuario_match_for_update = get_lista_usuario_match_for_update(openfire)
        if len(lista_usuario_match_for_update) == 0:
            print("N??o h?? usu??rios a serem alterados.")
        else:
            print("Valores a serem alterados:")
            pprint(lista_usuario_match_for_update)
            reposta = input("Deseja continuar? (S,N) :")
            if reposta.upper() == "S":
                run_update(openfire, lista_usuario_match_for_update)

if __name__ == "__main__":
    if len(argv) > 1:
        if argv[1] == "auto":
            main(automatico=True)
    else:
        main()
