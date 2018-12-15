





    @classmethod
    def index(cls, session, read, path):
        obj = session.query(Path).filter(cls.path==path).first()
        if obj == None or obj.out_of_date():
            if obj == None:
                obj = File(path=str(path.absolute()), mtime=_mtime(path))
                session.add(obj)
            else:
                for pair in obj.pairs:
                    for half in pair.halves:
                        session.delete(half)
                    session.delete(pair)
                session.flush()
            for i, line in enumerate(read(path)):
                pair = Pair(
                    source_file=obj, source_index=i,
                    part_of_speech=line['part_of_speech'],
                )
                session.add(pair)

                to_first = line['from_lang'] > line['to_lang']
                pair.halves.append(PairHalf(
                    pair=pair, first_lang=True,
                    lang=line['to_lang'] if to_first else line['from_lang'],
                    word=line['to_word'] if to_first else line['from_word'],
                ))
                pair.halves.append(PairHalf(
                    pair=pair, first_lang=False,
                    lang=line['from_lang'] if to_first else line['to_lang'],
                    word=line['from_word'] if to_first else line['to_word'],
                ))
            session.flush()

def index(session, format_names, data_directory):
    '''
    :param session: SQLAlchemy session
    :param format_names: Names of the dictionary format modules/subdirectories
    :param data_directory: Data directory
    '''
    for name in format_names:
        directory = data_directory / name
        if directory.is_dir():
            for file in directory.iterdir():
                File.index(session, file)
    session.commit()

def search(con, from_langs, to_langs, query):
    session.query(PairHalf) \
        .filter(PairHalf.lang.in_(from_langs))
    if not from_langs or not to_langs:
        ls = tuple(languages(con))
        if not from_langs:
            from_langs = sorted(set(l[0] for l in ls))
        if not to_langs:
            to_langs = sorted(set(l[1] for l in ls))
    pairs = tuple(product(from_langs, to_langs))

    start = min(len(alphabet.from_roman(query)) \
                for alphabet in ALPHABETS.values())
    encoded_queries = {}
    for i in range(start, MAX_PHRASE_LENGTH+1):
        results = []
        for from_lang, to_lang in pairs:
            if from_lang in encoded_queries:
                encoded_query = encoded_queries[from_lang]
            else:
                alphabet = ALPHABETS.get(from_lang, IDENTITY)
                encoded_query = alphabet.from_roman(query).encode('utf-8')
                encoded_queries[from_lang] = encoded_query
            lang_key = (from_lang.encode('ascii'), to_lang.encode('ascii'))
            key = b'lengths:%s:%s:%d' % (lang_key + (i,))
            for word_fragment in con.sscan_iter(key):
                if encoded_query in word_fragment:
                    key = b'phrase:%s:%s:%s' % (lang_key + (word_fragment,))
                    for definition in con.sscan_iter(key):
                        results.append(_line_loads(definition))
        yield from sorted(results, key=lambda line: line['to_word'])

def _line_dumps(x):
    return '\t'.join((
        x.get('part_of_speech', ''),
        x['from_word'], x['from_lang'],
        x['to_word'], x['to_lang'],
    )).encode('utf-8')
def _line_loads(x):
    y = {}
    y['part_of_speech'], y['from_word'], y['from_lang'], \
        y['to_word'], y['to_lang'] = x.decode('utf-8').split('\t')
    return y
