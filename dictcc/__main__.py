from . import download, look_up
import horetu

horetu.cli(horetu.Program([download, look_up], name='dict.cc'))
