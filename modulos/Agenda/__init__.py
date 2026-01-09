import json

evento = {
    "canal" : int,
    "cargo" : str,
    "tarefa" : str,
    "data" : str,
    "hora" : str
}

def load_agenda():
    with open('storage/agenda.json', 'r', encoding='utf-8') as file:
        return json.load(file)

#def add_task(server_id, cargo_id, tarefa, data, hora):
