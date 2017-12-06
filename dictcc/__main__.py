from . import download, look_up, ls
import horetu

horetu.cli(horetu.Program([
    ls,
    download,
    look_up,
], name='dict.cc'))
