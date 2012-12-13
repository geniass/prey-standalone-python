import sys
sys.path.append('/home/dotcloud/current')
from webapp.app import app as application

application.debug = True
application.config.update(DEBUG=True)
