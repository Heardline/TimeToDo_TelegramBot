import secret as cf

class Settings():
    cmd_welcome = 'command_text\cmd_welcome.html'
    cmd_menu = 'command_text\cmd_menu.html'
    admins = ()

class Auth():
      API_TOKEN = cf.TG_TOKEN
class db():  
    type_db = ''
    login = ''
    password = ''
    ip = ''
    table = ''
class vk():
    isuse = True
    VK_TOKEN = cf.VK_TOKEN
    skipads = True
    skipPostsWithCopyright = False
    reqFilter = ''
    reqVer = ''
    vkDomain = ''
    update = ''