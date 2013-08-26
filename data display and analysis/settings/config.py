import os

# default installation directories on Windows
skydrive_dir = 'SkyDrive'
data_dir = os.path.join(skydrive_dir, 'Documents/phd/0 - experiment/data')

def create_config():
    host_name = os.getenv('computername')
    user_dir = os.path.expanduser('~')
    user_data_dir = os.path.join(user_dir, data_dir)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    program_dir = os.path.dirname(script_dir)
    settings_dir = os.path.join(program_dir, 'settings')
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)
    with open(os.path.join(settings_dir, 'config.txt'), 'w') as f:
        f.write('data_dir: '+data_dir+'\n')

def prepare_analysis():
    host_name = os.getenv('computername')
    user_dir = os.path.expanduser('~')
    script_dir = os.path.dirname(os.path.realpath(__file__))
    program_dir = os.path.dirname(script_dir)
    settings_dir = os.path.join(program_dir, 'settings')
    config = {}
    try:
      with open(os.path.join(settings_dir, 'config.txt'), 'r') as f:
          lines = f.readlines()
          for line in lines:
              config[line.split(': ')[0].strip()] = line.split(': ')[1].strip()
    except:
        raise IOError
    user_data_dir = config['data_dir']
    analysis_dir = os.path.join(user_data_dir, 'analysis')
    if not os.path.exists(analysis_dir):
        os.makedirs(analysis_dir)

if __name__ == '__main__':
    create_config()
    prepare_analysis()
    