import os

if 'ENV' in os.environ and os.environ["ENV"] == "live":
    from envs.live import *
else:
    from envs.dev import *