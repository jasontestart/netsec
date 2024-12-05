import duo_client
import six.moves.configparser as ConfigParser

def my_admin_api():
  config_filename = 'duo.conf'
  config = ConfigParser.ConfigParser()
  config.read(config_filename)
  api_config = dict(config.items('duoadminapi'))

  return duo_client.Admin(
    ikey=api_config['ikey'],
    skey=api_config['skey'],
    host=api_config['host']
    )
