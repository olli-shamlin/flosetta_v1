
from app.model import Model


def kana_reference_tables():

    m = {c.romaji: c for c in Model().syllabary}

    tables = {
        'Basic': {
            ' ':   {'a': m['a'],   'i': m['i'],    'u': m['u'],   'e': m['e'],  'o': m['o']},
            'k':   {'a': m['ka'],  'i': m['ki'],   'u': m['ku'],  'e': m['ke'], 'o': m['ko']},
            's':   {'a': m['sa'],  'i': m['shi'],  'u': m['su'],  'e': m['se'], 'o': m['so']},
            't':   {'a': m['ta'],  'i': m['chi'],  'u': m['tsu'], 'e': m['te'], 'o': m['to']},
            'n':   {'a': m['na'],  'i': m['ni'],   'u': m['nu'],  'e': m['ne'], 'o': m['no']},
            'h':   {'a': m['ha'],  'i': m['hi'],   'u': m['fu'],  'e': m['he'], 'o': m['ho']},
            'm':   {'a': m['ma'],  'i': m['mi'],   'u': m['mu'],  'e': m['me'], 'o': m['mo']},
            'y':   {'a': m['ya'],  'i': None,      'u': m['yu'],  'e': None,    'o': m['yo']},
            'r':   {'a': m['ra'],  'i': m['ri'],   'u': m['ru'],  'e': m['re'], 'o': m['ro']},
            'w':   {'a': m['wa'],  'i': None,      'u': None,     'e': None,    'o': m['wo']},
            'n/m': {'a': m['n/m'], 'i': None,      'u': None,     'e': None,    'o': None},
        },
        'Dakuten': {
            'g': {'a': m['ga'], 'i': m['gi'],  'u': m['gu'],  'e': m['ge'], 'o': m['go']},
            'z': {'a': m['za'], 'i': m['ji'],  'u': m['zu'],  'e': m['ze'], 'o': m['zo']},
            'd': {'a': m['da'], 'i': m['dzi'], 'u': m['dzu'], 'e': m['de'], 'o': m['do']},
            'b': {'a': m['ba'], 'i': m['bi'],  'u': m['bu'],  'e': m['be'], 'o': m['bo']},
            'p': {'a': m['pa'], 'i': m['pi'],  'u': m['pu'],  'e': m['pe'], 'o': m['po']},
        },
        'Modified': {
            'ky': {'a': m['kya'], 'u': m['kyu'], 'o': m['kyo']},
            'gy': {'a': m['gya'], 'u': m['gyu'], 'o': m['gyo']},
            'sh': {'a': m['sha'], 'u': m['shu'], 'o': m['sho']},
            'jy':  {'a': m['jya'], 'u': m['jyu'], 'o': m['jyo']},
            'ch': {'a': m['cha'], 'u': m['chu'], 'o': m['cho']},
            'ny': {'a': m['nya'], 'u': m['nyu'], 'o': m['nyo']},
            'hy': {'a': m['hya'], 'u': m['hyu'], 'o': m['hyo']},
            'by': {'a': m['bya'], 'u': m['byu'], 'o': m['byo']},
            'my': {'a': m['mya'], 'u': m['myu'], 'o': m['myo']},
            'py': {'a': m['pya'], 'u': m['pyu'], 'o': m['pyo']},
            'ry': {'a': m['rya'], 'u': m['ryu'], 'o': m['ryo']},
        },
    }

    return tables
