import time
from modulos import Rank

estado = {
    'estudo' : True,
    'desligado' : False,
    'descanso' : None
}

all_pomodoros = {}

info_user = {
    'server_id' : None,
    'canal' : None,
    'msg' : None,
    'is_dm' : False,
    'embed_upd_timer' : 0,
    'pomodoro' : False,
    'blocos' : None,
    'time_start' : float,
    'temp_estudo' : int,
    'temp_descanso' : int
}


def start(server_id, user, canal_id, is_dm, blocos, estudo, descanso):
    if user not in all_pomodoros:
        all_pomodoros[user] = info_user.copy()

    if all_pomodoros[user]['pomodoro'] != estado['estudo']:

        all_pomodoros[user]['temp_estudo'] = estudo*60
        all_pomodoros[user]['temp_descanso'] = descanso*60

        all_pomodoros[user]['blocos'] = blocos
        all_pomodoros[user]['pomodoro'] = estado['estudo']
        all_pomodoros[user]['time_start'] = time.time()

        all_pomodoros[user]['server_id'] = server_id
        all_pomodoros[user]['canal'] = canal_id
        all_pomodoros[user]['is_dm'] = is_dm
        return True
    else:
        return False


def tempo(user):
    if user in all_pomodoros and all_pomodoros[user]['pomodoro'] != estado['desligado']:

        if all_pomodoros[user]['pomodoro'] == estado['estudo']:
            tempo_restante = (all_pomodoros[user]['temp_estudo'] - (time.time() - all_pomodoros[user]['time_start']))/60
            return (tempo_restante)
        
        elif all_pomodoros[user]['pomodoro'] == estado['descanso']:
            tempo_restante = (all_pomodoros[user]['temp_descanso'] - (time.time() - all_pomodoros[user]['time_start']))/60
            return (tempo_restante)
        
    else: return False


def stop(user):
    if user in all_pomodoros:
        all_pomodoros[user] = info_user.copy()
    else: return False


def verify_time_pomodoro(usr, inf):
    if inf['pomodoro'] == estado['estudo']:

        contagem = time.time() - inf['time_start']

        if contagem >= inf['temp_estudo']:

            inf['pomodoro'] = estado['descanso']
            inf['time_start'] = time.time()

            Rank.add_time_in_rank(usr, str(inf['server_id']), int(inf['temp_estudo']))
            return usr


    elif inf['pomodoro'] == estado['descanso']:

        contagem = time.time() - inf['time_start']

        if contagem >= inf['temp_descanso']:

            inf['pomodoro'] = estado['estudo']
            inf['time_start'] = time.time()
            inf['blocos'] -= 1
            return usr
        
    else:    
        return None

