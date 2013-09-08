import yaml

class FreeSwitchESLProtocolConfig(object):  

    def __init__(self):
        import yaml
        try:
            self.raw_config = yaml.load(file('config.yaml', 'r'))
        except:
            self.raw_config = {}
        
        self.dataDog = DataDogConfig(self.raw_config.get("DataDog", {}))
        
        self.freeSwitch = FreeSwitchConfig(self.raw_config.get("FreeSwitch", {}))

    def __repr__(self):
        return repr(self.raw_config)
            
class hostConfig(object):
    def __init__(self, values):
        self.raw_config = values
    
    def default_host(self):
        return "localhost"
    
    @property    
    def host(self):
        return self.raw_config.get("host", self.default_host())
    
    @property    
    def port(self):
        return self.raw_config.get("port", self.default_port())
        
    def __repr__(self):
        return repr(self.raw_config)    
                
class DataDogConfig(hostConfig):
    def __init__(self, values):
        hostConfig.__init__(self, values)
        
    def default_port(self):
        return 8125
    
    @property    
    def apiKey(self):
        return self.raw_config.get("API_KEY", None)

class FreeSwitchConfig(hostConfig):
    def __init__(self, values):
        hostConfig.__init__(self, values)

    def default_port(self):
        return 8021

    @property
    def password(self):
       return self.raw_config.get("API_KEY", "ClueCon")

    @property
    def normalHangupCauses(self):
        return self.raw_config.get("API_KEY", ["NORMAL_CLEARING"])

config = FreeSwitchESLProtocolConfig()