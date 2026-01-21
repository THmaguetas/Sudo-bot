import json

# carrega o json para o código
def load_rank():
    with open('storage/rank.json', 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)


def save_rank(infos):
    with open("storage/rank.json", "w", encoding="utf-8") as arquivo:
        json.dump(infos, arquivo, indent=4, ensure_ascii=False)


def add_in_rank(user_id, server_id):
    rank_list = load_rank()

    user_id = str(user_id)
    server_id = str(server_id)

    if server_id not in rank_list:
        rank_list[server_id] = {}

    if user_id not in rank_list[server_id]:
        rank_list.setdefault(server_id, {})
        rank_list[server_id][user_id] = {'quant_comandos' : 0, 'temp_estudo' : 0}

    if 'quant_comandos' not in user_id:
        rank_list[server_id][user_id].setdefault('quant_comandos', 0)

    rank_list[server_id][user_id]['quant_comandos'] += 1

    save_rank(rank_list)


def add_time_in_rank(user_id, server_id, tempo):
    rank_list = load_rank()

    user_id = str(user_id)
    server_id = str(server_id)
    tempo = int(tempo)

    if server_id not in rank_list:
        rank_list[server_id] = {}

    if user_id not in rank_list[server_id]:
        rank_list.setdefault(server_id, {})
        rank_list[server_id][user_id] = {'quant_comandos' : 0, 'temp_estudo' : 0}

    if 'temp_estudo' not in user_id:
        rank_list[server_id][user_id].setdefault('temp_estudo', 0)

    rank_list[server_id][user_id]['temp_estudo'] += tempo

    save_rank(rank_list)


def show_cmd_rank(server):
    rank_list = load_rank()

    server = str(server)

    if server not in rank_list:
        return []
    
    top3 = sorted(
        rank_list[server].items(), 
        key=lambda i: i[1]['quant_comandos'], 
        reverse=True
        )[:3]
    return top3  


def show_temp_rank(server):
    rank_list = load_rank()
    server = str(server)

    if server not in rank_list:
        return []

    valid_users = {
        user_id: info
        for user_id, info in rank_list[server].items()
        if info['temp_estudo'] > 0
    }
    if not valid_users:
        return []

    top3 = sorted(
        valid_users.items(),
        key=lambda i: i[1]['temp_estudo'],
        reverse=True
    )[:3]
    return top3

