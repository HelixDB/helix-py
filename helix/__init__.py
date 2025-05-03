# env vars?
# debug output on specific env var like DEBUG=1

# `python -c "import importlib.metadata as m; print(f'Total size: {sum([sum(f.locate().stat().st_blocks*512 for f in d.files) for d in m.distributions()]) / 1024 / 1024:.2f} MB')"` to see total size of installed packages

# TODO: get these correct once init version done
#   (don't do import *)

from helix.client import Client, Query
from helix.loader import Loader
from helix.types import Payload

__version__ = "0.1.0"