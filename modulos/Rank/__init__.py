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

    info_user = {
        'quant_comandos' : 0
    }

    if server_id not in rank_list:
        rank_list[server_id] = {}

    if user_id not in rank_list[server_id]:
        rank_list.setdefault(server_id, {})
        rank_list[server_id][user_id] = info_user
        
    rank_list[server_id][user_id]['quant_comandos'] += 1

    save_rank(rank_list)


def show_rank(server):
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
