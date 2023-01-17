import requests


class Openfire:
    def __init__(self, usuario, password, cooperativa, url):
        self.usuario = usuario
        self.password = password
        self.base_url = url
        self.cooperativa = cooperativa

    def openfire_api_get(self, query):
        headers = {"Accept": "application/json"}
        retorno = requests.get(
            self.base_url + query, headers=headers, auth=(self.usuario, self.password)
        )
        return retorno.json()

    def openfire_api_update(self, user, data):
        headers = {"Content-Type": "application/json"}
        retorno = requests.put(
            self.base_url + "/users/" + user,
            json=data,
            headers=headers,
            auth=(self.usuario, self.password),
        )
        return retorno

    def openfire_api_add(self, data):
        headers = {"Content-Type": "application/json"}
        retorno = requests.post(
            self.base_url + "/users/",
            json=data,
            headers=headers,
            auth=(self.usuario, self.password),
        )
        return retorno

    def openfire_api_add_user_group(self, user, group):
        headers = {"Content-Type": "application/json"}
        retorno = requests.post(
            self.base_url + "/users/" + user + "/groups/" + group,
            headers=headers,
            auth=(self.usuario, self.password),
        )
        return retorno

    def openfire_api_disable_user(self, user):
        headers = {"Content-Type": "application/json"}
        retorno = requests.post(
            self.base_url + "/lockouts/" + user,
            headers=headers,
            auth=(self.usuario, self.password),
        )
        return retorno

    def openfire_api_enable_user(self, user):
        headers = {"Content-Type": "application/json"}
        retorno = requests.delete(
            self.base_url + "/lockouts/" + user,
            headers=headers,
            auth=(self.usuario, self.password),
        )
        return retorno

    def get_all_users(self):
        users_dict = [
            usuario
            for usuario in self.openfire_api_get("/users")["users"]
            if self.cooperativa in usuario["username"]
        ]
        self.users_list = [
            [usuario["username"], usuario["name"]] for usuario in users_dict
        ]

    def search_users(self, query):
        lista_usuarios = []
        for usuario in self.users_list():
            if (
                query.strip().lower() in usuario["name"].strip().lower()
                and self.cooperativa in usuario["username"]
            ):
                lista_usuarios.append([usuario["username"], usuario["name"]])
        return lista_usuarios

    def update_user_name(self, user, username):
        data = {"name": username}
        retorno = self.openfire_api_update(user, data)
        return retorno

    def add_user(self, username, name, password):
        data = {"username": username, "name": name, "password": password}
        retorno = self.openfire_api_add(data)
        return retorno

    def add_user_group(self, user, group):
        retorno = self.openfire_api_add_user_group(user, group)
        return retorno

    def disable_user(self, user):
        retorno = self.openfire_api_disable_user(user)
        return retorno

    def enable_user(self, user):
        retorno = self.openfire_api_enable_user(user)
        return retorno
