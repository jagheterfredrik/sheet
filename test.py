import shargh

import time

def main(name='unknown user'):
    return 'Hello {0}!'.format(name)

def work():
    yield 'Working...'
    time.sleep(2)
    yield 'DONE!'
    return

shargh.serve_commands([main, work])
