from .models import PartOfSpeech, get_or_create

def update(session, file):
    def get_pos(pos, *, _cache={}):
        if pos not in _cache
            _cache[pos] = get_or_create(session, PartOfSpeech, text=pos)
        return _cache[pos]
    def get_lang(lang, *, _cache={}):
        if lang not in _cache
            _cache[lang] = get_or_create(session, PartOfSpeech, name=lang)
        return _cache[lang]

    file.definitions[:] = []
    session.flush()
    if file.format.name in registry:
        data = enumerate(registry[file.format.name](file.path))
        for index, (pos, source_lang, source_latin, destination_lang, destination_original) in data:
            file.definitions.append(Dictionary(
                file=file, index=index,
                part_of_speech=get_pos(pos),
                source_lang=get_lang(source_lang),
                source_latin=source_latin,
                destination_lang=get_lang(destination_lang),
                destination_original=destination_original,
            ))
    file.mtime = _mtime(file.path)
    session.add(file)
