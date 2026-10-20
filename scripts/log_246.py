"""Journal horodate de la francisation (ajout seul).

Chaque script du projet appelle `log(event, detail)` : une ligne par evenement,
avec l'heure locale. Le fichier vit dans <projet>/logs/francisation.log.
"""
import datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGDIR = os.path.join(ROOT, 'logs')
LOGFILE = os.path.join(LOGDIR, 'francisation.log')


def log(event, detail=''):
    os.makedirs(LOGDIR, exist_ok=True)
    line = f'{datetime.datetime.now().isoformat(timespec="seconds")}\t{event}\t{detail}\n'
    with open(LOGFILE, 'a', encoding='utf-8') as f:
        f.write(line)
    return line
