
import inspect
import datetime
from app import app
from markupsafe import Markup


def debug_msg(msg: str) -> None:
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    print(f'[DEBUG|{mod.__name__}>{frm.function}] {msg}')


def info_msg(msg: str) -> None:
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    print(f'[INFO|{mod.__name__}>{frm.function}] {msg}')


def error_msg(msg: str) -> None:
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    print(f'[INFO|{mod.__name__}>{frm.function}] {msg}')


def tracer(func):

    def wrapper(*args, **kwargs):

        # Get the second frame (frame_info instance actually) on the top of the stack
        stack = inspect.stack()
        frame_info = stack[1]

        # Extract the info we want to include on the trace line from the frame
        fnc_name = func.__name__
        fname_split = func.__globals__['__file__'].split('/')
        filename = fname_split[-1]  # frame_info.filename.split('/')[-1]
        if filename == '__init__.py':
            filename = fname_split[-2] + '/' +  filename

        mod_name = '__main__'
        if __name__ != '__main__':
            mod_name = func.__module__  # inspect.getmodule(frame_info[0]).__name__

        cls_name = ''
        if args:
            mbrs = dict(inspect.getmembers(args[0]))
            if '__class__' in mbrs.keys():
                cls_name = mbrs['__class__'].__name__ + '.'

        msg = f'{filename}: {mod_name}.{cls_name}{fnc_name}()'

        print(f'[TRACER] ⬇︎ entering {msg}')
        answer = func(*args, **kwargs)
        print(f'[TRACER] ⬆︎ exiting {msg}')
        return answer

    return wrapper


def _now() -> str:
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')


class _FilePath:

    def __init__(self, path: str, name: str, ext: str):
        self.name: str = name
        self.extension: str = ext

        # The current directory varies depending on the runtime context (i.e., whether the Flask app is being
        # run or the pytest suite.) So we're just going to hack resolution of the path here. Note this means
        # this routine expects the value of the path argument to be a relative path expression.
        self.path = f'{app.root_path}/{path}'
        return

    @property
    def full_path(self) -> str:
        return f'{self.path}/{self.name}.{self.extension}'


class FilePaths:
    _local_path = 'data'
    _backup_path = 'data/backups'
    _prod_database_name = 'rosetta'
    _test_database_name = 'test_rosetta'
    _database_extension = 'sqlite3'
    _vocab_spreadsheet_name = 'vocabulary'
    _kana_spreadsheet_name = 'kana'
    _spreadsheet_extension = 'numbers'

    prod_database = _FilePath(_local_path,  _prod_database_name, _database_extension)
    test_database = _FilePath(_local_path, _test_database_name, _database_extension)
    glob_database = _FilePath(_backup_path, f'{prod_database.name}-*', prod_database.extension)
    backup_database = _FilePath(_backup_path, f'{prod_database.name}-{_now()}', prod_database.extension)
    vocab_spreadsheet = _FilePath(_local_path, _vocab_spreadsheet_name, _spreadsheet_extension)
    glob_vocab = _FilePath(_backup_path, f'{vocab_spreadsheet.name}-*', vocab_spreadsheet.extension)
    backup_vocab = _FilePath(_backup_path, f'{vocab_spreadsheet.name}-{_now()}', vocab_spreadsheet.extension)
    kana_spreadsheet = _FilePath(_local_path, _kana_spreadsheet_name, _spreadsheet_extension)
    glob_kana = _FilePath(_backup_path, f'{kana_spreadsheet.name}-*', kana_spreadsheet.extension)
    backup_kana = _FilePath(_backup_path, f'{kana_spreadsheet.name}-{_now()}', kana_spreadsheet.extension)


def resolve_icon(name: str) -> str:

    icon_map = {
        'robot': Markup('xmlns="http://www.w3.org/2000/svg" width="40" height="32" fill="currentColor" '
                        'class="bi bi-robot" viewBox="0 0 16 16">'
                        '<path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 '
                        '6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 '
                        '0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.'
                        '827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.'
                        '149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 '
                        '25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.'
                        '076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/><path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 '
                        '4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 '
                        '1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.'
                        '5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"'),
        'backpack': Markup('xmlns="http://www.w3.org/2000/svg" width="40" height="32" fill="currentColor" '
                           'class="bi bi-backpack3" viewBox="0 0 16 16">'
                           '<path d="M4.04 7.43a4 4 0 0 1 7.92 0 .5.5 0 1 1-.99.14 3 3 0 0 0-5.94 0 .5.5 0 1 1-.99-.'
                           '14M4 9.5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5h-7a.5.5 0 0 1-.5-.5zm1 .'
                           '5v3h6v-3h-1v.5a.5.5 0 0 1-1 0V10z"/><path d="M6 2.341V2a2 2 0 1 1 4 0v.341c.465.165.904.'
                           '385 1.308.653l.416-1.247a1 1 0 0 1 1.748-.284l.77 1.027a1 1 0 0 1 .15.917l-.803 2.407C13.'
                           '854 6.49 14 7.229 14 8v5.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 2 13.5V8c0-.771.146-1.'
                           '509.41-2.186l-.802-2.407a1 1 0 0 1 .15-.917l.77-1.027a1 1 0 0 1 1.748.284l.416 1.247A6 '
                           '6 0 0 1 6 2.34ZM7 2v.083a6 6 0 0 1 2 0V2a1 1 0 1 0-2 0m5.941 2.595.502-1.505-.77-1.027-.'
                           '532 1.595q.447.427.8.937M3.86 3.658l-.532-1.595-.77 1.027.502 1.505q.352-.51.8-.937M8 3a5 '
                           '5 0 0 0-5 5v5.5A1.5 1.5 0 0 0 4.5 15h7a1.5 1.5 0 0 0 1.5-1.5V8a5 5 0 0 0-5-5"'),
        'brilliance': Markup('xmlns="http://www.w3.org/2000/svg" width="40" height="32" fill="currentColor" '
                             'class="bi bi-brilliance" viewBox="0 0 16 16"><path d="M8 16A8 8 0 1 1 8 0a8 8 0 0 1 0 '
                             '16M1 8a7 7 0 0 0 7 7 3.5 3.5 0 1 0 0-7 3.5 3.5 0 1 1 0-7 7 7 0 0 0-7 7"/>'),
        'speedometer2': Markup('xmlns="http://www.w3.org/2000/svg" width="40" height="32" fill="currentColor" '
                               'class="bi bi-speedometer2" viewBox="0 0 16 16">'
                               '<path d="M8 4a.5.5 0 0 1 .5.5V6a.5.5 0 0 1-1 0V4.5A.5.5 0 0 1 8 4M3.732 5.732a.5.5 0 0 '
                               '1 .707 0l.915.914a.5.5 0 1 1-.708.708l-.914-.915a.5.5 0 0 1 0-.707M2 10a.5.5 0 0 1 '
                               '.5-.5h1.586a.5.5 0 0 1 0 1H2.5A.5.5 0 0 1 2 10m9.5 0a.5.5 0 0 1 .5-.5h1.5a.5.5 0 0 1 0 '
                               '1H12a.5.5 0 0 1-.5-.5m.754-4.246a.39.39 0 0 0-.527-.02L7.547 9.31a.91.91 0 1 0 1.302 '
                               '1.258l3.434-4.297a.39.39 0 0 0-.029-.518z"/><path fill-rule="evenodd" d="M0 10a8 8 0 1 '
                               '1 15.547 2.661c-.442 1.253-1.845 1.602-2.932 1.25C11.309 13.488 9.475 13 8 13c-1.474 '
                               '0-3.31.488-4.615.911-1.087.352-2.49.003-2.932-1.25A8 8 0 0 1 0 10m8-7a7 7 0 0 0-6.603 '
                               '9.329c.203.575.923.876 1.68.63C4.397 12.533 6.358 12 8 12s3.604.532 4.923.96c.757.245 '
                               '1.477-.056 1.68-.631A7 7 0 0 0 8 3"/>'),
        'question': Markup('xmlns="http://www.w3.org/2000/svg" width="40" height="32" fill="currentColor" '
                           'class="bi bi-question-octagon" viewBox="0 0 16 16"><path d="M4.54.146A.5.5 0 0 1 '
                           '4.893 0h6.214a.5.5 0 0 1 .353.146l4.394 4.394a.5.5 0 0 1 .146.353v6.214a.5.5 0 0 '
                           '1-.146.353l-4.394 4.394a.5.5 0 0 1-.353.146H4.893a.5.5 0 0 1-.353-.146L.146 '
                           '11.46A.5.5 0 0 1 0 11.107V4.893a.5.5 0 0 1 .146-.353zM5.1 1 1 5.1v5.8L5.1 15h5.'
                           '8l4.1-4.1V5.1L10.9 1z"/><path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 '
                           '.248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 '
                           '.635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 '
                           '.25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 '
                           '1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 '
                           '2.286m1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-'
                           '.94-1.029-.94-.584 0-1.009.388-1.009.94"/>'),
    }

    assert name in icon_map.keys()
    return icon_map[name]
