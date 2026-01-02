import sys
import platform

if tuple(map(int, platform.python_version_tuple())) <= (3, 13):
    raise RuntimeError('Invalid minimum Python version. Expecting >= 3.13.')

if __name__ == '__main__':
    import app
    sys.exit(app.main(sys.argv[1:]))
