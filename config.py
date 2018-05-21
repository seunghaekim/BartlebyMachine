import os, yaml

class ConfigClass:
    config_file     = 'config.yaml'
    manuscript_dir  = os.path.join(os.getcwd(), 'manuscript')
    template    = None
    latex_dir   = None

    def __init__(self, config_file):
        config_file = os.path.join(os.getcwd(), config_file)
        config = self.readConfig()
        self.latex_dir = os.path.join(self.manuscript_dir, 'tex')
        os.makedirs(self.latex_dir, exist_ok=True)

        for key in config:
            if key == 'template':
                config[key] = os.path.join(os.getcwd(), 'BartlebyMachine', config[key]) + '.tex'
                f = open(config[key], mode='r', encoding='utf-8')
                template = f.read()
                f.close()
                config[key] = template

            setattr(self, key, config[key])


        return


    def readConfig(self):
        result = False

        try:
            with open(self.config_file, encoding='utf-8') as config:
                config = yaml.load(config)
        except:
            return False

        return config


def Config():
    return ConfigClass('config.yaml')
