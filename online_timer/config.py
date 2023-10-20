
import json
from mcdreforged.api.all import *
from online_timer.util import psi

logger = psi.psi.logger

config = psi.psi.load_config_simple(default_config={
        'max_oltop': 10
    })

logger.info('Reloaded Config:')
logger.info(json.dumps(config, indent=2))


