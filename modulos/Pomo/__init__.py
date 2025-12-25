import time

estado = {
    'estudo' : True,
    'desligado' : False,
    'descanso' : None
}

all_pomodoros = {}

info_user = {
    'pomodoro' : False,
    'time_start' : None,
    'temp_estudo' : int(25*60),
    'temp_descanso' : int(5*60)
}


def start(user, canal_id):
    if user not in all_pomodoros:
        all_pomodoros[user] = info_user.copy()

    info = all_pomodoros[user]
    info['canal_id'] = canal_id

    if all_pomodoros[user]['pomodoro'] != estado['estudo']:
        all_pomodoros[user]['pomodoro'] = estado['estudo']
        all_pomodoros[user]['time_start'] = time.time()
        return True
    else:
        return False


def tempo(user):
    if user in all_pomodoros and all_pomodoros[user]['pomodoro'] != estado['desligado']:

        if all_pomodoros[user]['pomodoro'] == estado['estudo']:
            tempo_restante = (all_pomodoros[user]['temp_estudo'] - (time.time() - all_pomodoros[user]['time_start']))/60
            return f'**ESTUDO**: {tempo_restante:.1f}'
        
        elif all_pomodoros[user]['pomodoro'] == estado['descanso']:
            tempo_restante = (all_pomodoros[user]['temp_descanso'] - (time.time() - all_pomodoros[user]['time_start']))/60
            return f'**DESCANSO**: {tempo_restante:.1f}'
        
    else: False


def stop(user):
    if user in all_pomodoros:
        all_pomodoros[user]['pomodoro'] = estado['desligado']
        all_pomodoros[user]['time_start'] = estado['descanso']
    else: False


def verify_time_pomodoro():
    for user, info in all_pomodoros.items():
        if info['pomodoro'] == estado['estudo']:
            contagem = time.time() - info['time_start']
            if contagem >= info['temp_estudo']:
                info['pomodoro'] = estado['descanso']
                info['time_start'] = time.time()
                return user
        
        elif info['pomodoro'] == estado['descanso']:
            contagem = time.time() - info['time_start']
            if contagem >= info['temp_descanso']:
                info['pomodoro'] = estado['estudo']
                info['time_start'] = time.time()
                return user
    return None

