from .cardxml import parse_carddefs, write_db

import os
import subprocess

def capture_stdout(*args, **kvargs):
    env = dict(os.environ)
    env.update(kvargs)
    proc = subprocess.Popen(args, env=env, stdout=subprocess.PIPE)
    stdout_data, stderr_data = proc.communicate()
    if proc.returncode == 0:
        return stdout_data.decode('utf8').rstrip('\n')
    else:
        raise OSError('Subprocess returned {0}'.format(proc.returncode))

def update_cards():
    """Updates the cards definition using the XML data from the hs-data repo.
    """

    # Capture version information of data used.
    url = capture_stdout(
            'git', 'config', '--file', '.gitmodules', 'submodule.hs-data.url'
            )
    commit = capture_stdout(
            'git', 'rev-parse', '@', GIT_DIR='hs-data/.git'
            )
    comment = 'Generated from {0} (commit {1})'.format(url, commit[:10])

    # Read card data.
    cards = parse_carddefs('hs-data/CardDefs.xml')

    # Rewrite the 'carddefs' module.
    with open('hearthy/db/carddefs.py', 'w') as f:
        print("'''\n{0}\n'''".format(comment), file=f)
        print(file=f)
        write_db(cards, f)

if __name__ == '__main__':
    update_cards()
