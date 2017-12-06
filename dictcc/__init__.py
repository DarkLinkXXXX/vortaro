
def download():
    import sys, webbrowser
    sys.stdout.write('''\
The download page will open in a web browser. Download the dictionary
of interest (as zipped text), unzip it, and save the text file as this:
~/.dict.cc/[from language]-[to language].txt

Press enter when you are ready.
''')
    input()
    webbrowser.open('https://www1.dict.cc/translation_file_request.php?l=e')
