import os, sys, platform, subprocess

if os.name == 'nt':
    import pywinpty

class PTYProcess:
    def __init__(self, argv, cwd=None, env=None, cols=80, rows=24):
        if os.name == 'nt':
            self._spawn_windows(argv, cwd, env, cols, rows)
        else:
            self._spawn_unix(argv, cwd, env, cols, rows)

    # ---------- Unix ----------
    def _spawn_unix(self, argv, cwd, env, cols, rows):
        import pty, fcntl, termios, struct
        master, slave = pty.openpty()
        subprocess_env = env or os.environ.copy()
        subprocess_env.setdefault("TERM", "xterm-256color")

        self.proc = subprocess.Popen(
            argv,
            stdin=slave, stdout=slave, stderr=slave,
            cwd=cwd, env=subprocess_env, close_fds=True
        )
        os.close(slave)
        # size
        fcntl.ioctl(
            master, termios.TIOCSWINSZ,
            struct.pack("HHHH", rows, cols, 0, 0)
        )
        self.fd = master

    # ---------- Windows ----------
    def _spawn_windows(self, argv, cwd, env, cols, rows):
        winpty = pywinpty.WinPTY(cols=cols, rows=rows)
        subprocess_env = env or os.environ.copy()
        subprocess_env.setdefault("TERM", "xterm-256color")
        subprocess_env.setdefault("COLORTERM", "truecolor")

        winpty.spawn(argv, cwd=cwd, env=subprocess_env)
        self.proc = winpty
        self.fd   = winpty.fileno()        # works with os.read/os.write

    # unified API
    def fileno(self):          # so select() works
        return self.fd

    def read(self, n=1024):
        import os
        return os.read(self.fd, n)

    def write(self, data: bytes):
        import os
        os.write(self.fd, data)

    def alive(self):
        return self.proc.isalive() if os.name == 'nt' else (self.proc.poll() is None)

    def terminate(self):
        self.proc.terminate()
