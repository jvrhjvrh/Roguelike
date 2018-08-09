import tdl

class GameObject:
    def __init__(self,x,y,char,color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
    
    def move(self,dx,dy):
        if not my_map[self.x + dx][self.y +dy].blocked:
            self.x += dx
            self.y += dy
    
    def draw (self):
        con.draw_char(self.x,self.y,self.char,self.color)
    
    def clear(self):
        con.draw_char(self.x,self.y,' ',self.color,bg = None)
class Tile:
    def __init__(self,blocked,block_sight = None):
        self.blocked = blocked
        if(block_sight is None): block_sight = blocked
        self.block_sight = block_sight
class Rect:
    def __init__(self,x,y,w,h):
        self.x1 = x
        self.y1 = y
        self.x2 = x+w
        self.y2 = y+h

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
color_dark_wall = (0, 0, 100)
color_dark_ground = (50, 50, 150)
my_map = []

def create_room(room):
    global my_map

    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False

def make_map():
    global my_map

    my_map = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    room1 = Rect(20, 15, 10, 15)
    room2 = Rect(50, 15, 10, 15)
    create_room(room1)
    create_room(room2)

def render_all():
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = my_map[x][y].block_sight
            if wall:
                con.draw_char(x,y,None, fg = None, bg = color_dark_wall)
            else:
                con.draw_char(x,y,None,fg = None, bg = color_dark_ground)
    
    for obj in objects:
        obj.draw()

    root.blit(con,0,0,SCREEN_WIDTH,SCREEN_HEIGHT,0,0)


def handle_keys():

    user_input = tdl.event.key_wait()

    if user_input.key == "ENTER" and user_input.alt:
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE":
        return True
    
    if user_input.key == "UP":
        player.move(0,-1)
    elif user_input.key == "DOWN":
        player.move(0,1)
    elif user_input.key == "LEFT":
        player.move(-1,0)
    elif user_input.key == "RIGHT":
        player.move(1,0)

tdl.set_font('arial10x10.png',greyscale = True, altLayout = True)
root = tdl.init(SCREEN_WIDTH,SCREEN_HEIGHT,title = "Roguelike",fullscreen = False)
con = tdl.Console(SCREEN_WIDTH,SCREEN_HEIGHT)
player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, '@', (255,255,255))
npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, '@', (255,255,0))
objects = [npc, player]

make_map()
player.x = 25
player.y = 23
while not tdl.event.is_window_closed():
    render_all()
    tdl.flush()
    
    for obj in objects:
        obj.clear()
    exit_game = handle_keys()
    if (exit_game == True):
        break

