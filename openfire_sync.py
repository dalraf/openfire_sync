import requests
from io import BytesIO
import pandas as pd
from openfire import Openfire
import jellyfish
from config import (
    planilha_url,
    openfire_password,
    cooperativa_code,
    openfire_api,
    openfire_user,
)


def get_file_data(url):
    response = requests.get(url)
    
    with BytesIO() as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
        f.seek(0)
        
        # Copie os dados para uma nova variável antes de sair do bloco 'with'
        file_data = f.getvalue()

    return BytesIO(file_data)



def get_openfire_object():
    openfire = Openfire(
        openfire_user, openfire_password, cooperativa_code, openfire_api
    )
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


def process_line(line):
    nome = line[1][2].strip()
    if not nome:
        return None

    cargo = line[1][1].strip()
    ramal = line[1][4] if line[1][3] != "*" else ""
    telefone = (
        line[1][3] if "Apenas Ramal" not in line[1][2] and "*" not in line[1][2] else ""
    )
    celular = str(line[1][5])

    # Formatar string de celular para o padrão (xx) xxxxx-xxxx
    if len(celular) == 11:
        celular = f"({celular[0:2]}) {celular[2:7]}-{celular[7:]}"

    return [nome, cargo, ramal, telefone, celular]


def get_users_for_update():
    planilha_coopemg = get_planilha_coopemg()
    lista_users_for_update = []

    for linha in planilha_coopemg.iterrows():
        try:
            user_data = process_line(linha)
            if user_data:
                nome, cargo, ramal, telefone, celular = user_data

                if lista_users_for_update and lista_users_for_update[-1][0] == nome:
                    if ramal != "*":
                        lista_users_for_update[-1][2] += f"/ {ramal}"
                else:
                    lista_users_for_update.append(
                        [nome, cargo, ramal, telefone, celular]
                    )

        except Exception as e:
            print(linha)
            print(e.args[0])
            exit(1)

    return lista_users_for_update


def format_contact_info(row):
    setor = f" - {str(row[1])}" if row[1] else " - Sem Setor"
    ramal_interno = f" - {str(row[2]).strip()}" if str(row[2]).strip() not in ["", "*"] else ""
    telefone_fixo = f" - {str(row[3]).strip()}" if str(row[3]).strip() not in ["", "*"] else ""
    celular = f" / {str(row[4]).strip()}" if str(row[4]).strip() not in ["", "*"] else ""

    return setor, ramal_interno, telefone_fixo, celular



def find_best_match(nome_search, openfire):
    best_similarity = 0
    best_match = None

    for user in openfire.users_list:
        nome_real = user[1].strip().replace("–", "-").split("-")[0].strip()
        similarity = jellyfish.jaro_similarity(nome_search, nome_real)

        if similarity > best_similarity:
            best_match = {
                'nome_certo': nome_search,
                'id': user[0],
                'similarity': similarity,
                'descricao_antiga': user[1]
            }
            best_similarity = similarity

    return best_match


def get_lista_usuario_match_for_update(openfire):
    lista_users_for_update = get_users_for_update()
    lista_usuario_match_for_update = []

    for row in lista_users_for_update:
        nome_search = str(row[0])

        if not any(i in nome_search for i in ["Sem Atendente", "*"]):
            setor, ramal_interno, telefone_fixo, celular = format_contact_info(row)
            contato = ramal_interno + telefone_fixo + celular
            best_match = find_best_match(nome_search, openfire)

            if best_match and best_match['similarity'] > 0.9:
                descricao_nova = best_match['nome_certo'] + setor + contato

                if descricao_nova != best_match['descricao_antiga']:
                    lista_usuario_match_for_update.append(
                        [best_match['id'], best_match['descricao_antiga'], descricao_nova]
                    )

    return lista_usuario_match_for_update


def run_update(openfire, lista_usuario_match_for_update):
    total_users = len(lista_usuario_match_for_update)
    for idx, user in enumerate(lista_usuario_match_for_update, start=1):
        user_id, old_desc, new_desc = user
        print(f"({idx}/{total_users}) Alterando usuário: {user_id}")
        print(f"Descrição antiga: {old_desc}")
        print(f"Descrição nova: {new_desc}")
        
        retorno = openfire.update_user_name(user_id, new_desc)
        
        print(f"Usuário {user_id}: {retorno}\n")


def retorna_lista():
    openfire = get_openfire_object()
    lista_usuario_match_for_update = get_lista_usuario_match_for_update(openfire)
    return openfire, lista_usuario_match_for_update


def executa_lista(openfire, lista_usuario_match_for_update):
    run_update(openfire, lista_usuario_match_for_update)
