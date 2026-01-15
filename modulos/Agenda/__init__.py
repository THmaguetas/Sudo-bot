import json
import time
from datetime import datetime

# carrega o json para o código
def load_agenda():
    with open('storage/agenda.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def save_agenda(infos):
    with open("storage/agenda.json", "w", encoding="utf-8") as arquivo:
        json.dump(infos, arquivo, indent=4, ensure_ascii=False)


def add_task(server_id, cargo_id, tarefa, desc, data_hora, canal):
    agenda_json = load_agenda()
    
    evento_id = str(time.time())
    itens_evento = {
        "canal" : canal,
        "cargo" : cargo_id,
        "tarefa" : tarefa,
        "descricao" : desc,
        "data_hora" : data_hora,
        "notificado" : False
    }

    if server_id not in agenda_json:
        agenda_json.setdefault(server_id, {})
        agenda_json[server_id][evento_id] = itens_evento

    else: 
        agenda_json[server_id][evento_id] = itens_evento

    save_agenda(agenda_json)


def valid_data(data, time):
    data_hora = f'{data} {time}'
    try:
        datetime.strptime(str(data), '%d/%m/%Y')
        datetime.strptime(str(time), '%H:%M')

        try_data_hora = datetime.strptime(f"{data} {time}", "%d/%m/%Y %H:%M")
        agora = datetime.now()
        if try_data_hora < agora:
            return False

        return data_hora
    
    except ValueError:
        return False


def list_agenda(server_id, cargo_id=None):
    agenda_json = load_agenda()

    eventos_validos = []
    eventos_validos.clear()

    if cargo_id == None:
        for evento_id, itens in agenda_json[server_id].items():
            if itens['notificado'] is False:
                eventos_validos.append(itens["tarefa"])
                
    else:
        for evento_id, itens in agenda_json[server_id].items():
            if itens['notificado'] is False and itens['cargo'] == cargo_id:
                eventos_validos.append(itens["tarefa"])
    
    return eventos_validos

