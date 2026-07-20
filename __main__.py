import sys
import platform
import importlib

if tuple(map(int, platform.python_version_tuple())) <= (3, 13):
    raise RuntimeError('Invalid minimum Python version. Expecting >= 3.13.')

if __name__ == '__main__':
    app = importlib.import_module('app')
    sys.exit(app.main(app.parse_args(sys.argv[1:])))
