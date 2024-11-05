
import sys
from app.model.dbms import create
from app.utils.exceptions import RosettaError


if __name__ == '__main__':

    try:
        create()
    except RosettaError as e:
        print(f'ERROR: {e.message}')
        print(f'ERROR: exiting')
        sys.exit(1)

    sys.exit(0)
