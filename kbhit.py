import sys
import termios
import atexit
from select import select

class KBHit:
    """
        A Python class implementing KBHIT, the standard keyboard-interrupt poller.
        Works transparently on Windows and Posix (Linux, Mac OS X).  Doesn't work with IDLE.
    """
    def __init__(self):
        '''
            Creates a KBHit object that you can call to do various keyboard things.
        '''
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
        atexit.register(self.set_normal_term)

    def set_normal_term(self):
        '''
            Resets to normal terminal.  On Windows this is a no-op.
        '''
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def kbhit(self):
        '''
            Returns True if keyboard character was hit, False otherwise.
        '''
        dr, _, _ = select([sys.stdin], [], [], 0)
        return dr != []
