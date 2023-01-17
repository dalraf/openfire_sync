import requests
from io import BytesIO
import pandas as pd
from openfire import Openfire
import jellyfish
from pprint import pprint
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


openfire = Openfire(openfire_user, openfire_password, cooperativa_code, openfire_api)
openfire.get_all_users()

coopemg_arquivo_data = get_file_data(planilha_url)
planilha_coopemg = pd.read_excel(
    coopemg_arquivo_data, skiprows=6, index_col=None, header=None
)
planilha_coopemg = planilha_coopemg.dropna(axis=0)

lista_users_update_add = []
for j in planilha_coopemg.iterrows():
    nome = j[1][1].strip()
    cargo = j[1][0].strip()
    ramal = j[1][3] if j[1][3] != "*" else ""
    telefone = j[1][2] if "Apenas Ramal" not in j[1][2] and "*" not in j[1][2] else ""
    celular = j[1][4] if j[1][4] != "*" else ""
    lista_users_update_add.append([nome, cargo, ramal, telefone, celular])


lista_usuario_search = []
for row in lista_users_update_add:
    nome_search = row[0]
    setor = row[1]
    if str(row[2]) != "" and row[3] != "" and row[4] != "":
        ramal = "ramal " + str(row[2]) + " - " + str(row[3]) + " / " + str(row[4])
    elif str(row[2]) != "" and row[3] != "" and row[4] == "":
        ramal = "ramal " + str(row[2]) + " - " + str(row[3])
    elif str(row[2]) != "" and row[3] == "" and row[4] != "":
        ramal = "ramal " + str(row[2]) + " / " + str(row[4])
    elif str(row[2]) != "" and row[3] == "" and row[4] == "":
        ramal = "ramal " + str(row[2])
    elif str(row[2]) == "" and row[3] != "" and row[4] != "":
        ramal = "ramal " + str(row[3]) + " / " + str(row[4])
    elif str(row[2]) == "" and row[3] == "" and row[4] != "":
        ramal = "ramal " + str(row[4])
    else:
        ramal = ""
    semelhanca_maior = 0
    for user in openfire.users_list:
        nome_real = user[1].strip().replace("–", "-").split("-")[0].strip()
        semelhanca = jellyfish.jaro_similarity(nome_search, nome_real)
        if semelhanca > semelhanca_maior:
            nome_certo = nome_search
            descricao_antiga = user[1]
            id = user[0]
            semelhanca_maior = semelhanca
    if ramal != "":
        descricao = " ".join(
            [
                nome_certo,
                "-",
                setor,
                "-",
                ramal,
            ]
        )
    else:
        descricao = " ".join([nome_certo, "-", setor])
    diferenca = descricao == descricao_antiga
    lista_usuario_search.append([id, descricao, descricao_antiga, diferenca])

lista_usuario_search = [i for i in lista_usuario_search if i[3] == False]

print("Valores a serem alterados:")
pprint(lista_usuario_search)

reposta = input("Deseja continuar? (S,N) :")

if reposta.upper() == "S":
    for user in lista_usuario_search:
        openfire.update_user_name(user[0], user[1])
