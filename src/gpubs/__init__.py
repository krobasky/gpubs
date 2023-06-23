__version__ = "unknown"
try:
    from gpubs import _version

    __version__ = _version.__version__
except ImportError:
    pass
