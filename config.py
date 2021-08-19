

class Settings():
    def __init__(self) -> None:
        self.cmd_welcome = ''
        self.cmd_menu = ''
        self.admins = ()

class Auth():
    def __init__(self) -> None:    
        self.API_TOKEN = ''
        
class db():
    def __init__(self) -> None:  
        self.type_db = ''
        self.login = ''
        self.password = ''
        self.ip = ''
        self.table = ''
class vk():
    def __init__(self) -> None:
        self.isuse = True
        self.VK_TOKEN = ''
        self.skipads = True
        self.skipPostsWithCopyright = False
        self.reqFilter = ''
        self.reqVer = ''
        self.vkDomain = ''
        self.update = ''