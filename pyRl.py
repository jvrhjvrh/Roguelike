import tdl
from random import randint
import colors
import math
import textwrap

class GameObject:
    def __init__(self,x,y,char,name,color, blocks = False, fighter = None, ai = None):
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.blocks = blocks
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
    
    def move(self,dx,dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def draw (self):
        global visible_tiles
        if(self.x, self.y) in visible_tiles:
            con.draw_char(self.x,self.y,self.char,self.color)
    
    def clear(self):
        con.draw_char(self.x,self.y,' ',self.color,bg = None)

    def move_towards(self,target_x,target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx/distance))
        dy = int(round(dy/distance))

        self.move(dx,dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy **2)

    def send_to_back(self):
        global objects

        objects.remove(self)
        objects.insert(0,self)

    class Fighter:
        def __init__(self, hp, defense, power, death_function = None):
            self.max_hp = hp
            self.hp = hp
            self.defense = defense
            self.power = power
            self.death_function = death_function

        def take_damage(self, damage):
            if damage > 0:
                self.hp -= damage
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)
        
        def attack(self, target):
            damage = self.power - target.fighter.defense

            if damage > 0:
                print(self.owner.name.capitalize() + " attacks " + target.name + " for " + str(damage) + " hit points")
                target.fighter.take_damage(damage)
            else:
                print(self.owner.name.capitalize() + " attacks " + target.name + " but it has no effect " )
    class BasicMonster:
        def take_turn(self):
            monster = self.owner

            if(monster.x, monster.y) in visible_tiles:

                if monster.distance_to(player) >= 2:
                    monster.move_towards(player.x,player.y)
                elif player.fighter.hp >0:
                    monster.fighter.attack(player)
    
class Tile:
    def __init__(self,blocked,block_sight = None):
        self.blocked = blocked
        if(block_sight is None): block_sight = blocked
        self.block_sight = block_sight
        self.explored = False
class Rect:
    def __init__(self,x,y,w,h):
        self.x1 = x
        self.y1 = y
        self.x2 = x+w
        self.y2 = y+h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x,center_y)

    def intersect(self,other):
        #retorna verdadeiro se intersectar com outro retangulo
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)


FOV_ALGO = "BASIC"
FOV_LIGHT_WALLS = True
LIMIT_FPS = 20
TORCH_RADIUS = 10
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 43
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH -2
MSG_HEIGHT = PANEL_HEIGHT - 1


color_dark_wall = (0, 0, 100)
color_light_wall = (130, 110, 50)
color_dark_ground = (50, 50, 150)
color_light_ground = (200, 180, 50)
color_dead_char = (191,0,0)
color_red = (255,0,0)
color_black = (0,0,0)
color_white = (0,0,0)
color_light_red = (255,115,115)
color_dark_red =(191,0,0)
color_light_grey = (159,159,159)

my_map = []
game_msgs = []

fov_recompute = True

def is_visible_tile(x, y):
    global my_map

    if x >= MAP_WIDTH or x < 0:
        return False
    elif y>= MAP_HEIGHT or y < 0:
        return False
    elif my_map[x][y].blocked == True:
        return False
    elif my_map[x][y].block_sight == True:
        return False
    else:
        return True

def create_room(room):
    global my_map

    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False

def place_objects(room):
    num_monsters = randint(0,MAX_ROOM_MONSTERS)
    for i in range(num_monsters):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        
        if not is_blocked(x,y):
            if(randint(0,100) < 80):
                fighter_component = GameObject.Fighter(hp = 10, defense =  0, power = 3,death_function= monster_death)
                ai_component = GameObject.BasicMonster()
                monster = GameObject(x,y,"o","Orc",(64,128,64),True,fighter= fighter_component, ai= ai_component)
            else:
                fighter_component = GameObject.Fighter(hp = 16, defense = 1, power = 4, death_function = monster_death)
                ai_component =  GameObject.BasicMonster()
                monster = GameObject(x,y,"T","Troll",(0,128,0),True, fighter = fighter_component, ai= ai_component)
        
            objects.append(monster)

def make_map():
    global my_map
    rooms = []
    num_rooms = 0

    my_map = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    for r in range(MAX_ROOMS):
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE,ROOM_MAX_SIZE)
        x = randint(0, MAP_WIDTH - w - 1)
        y = randint(0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if(new_room.intersect(other_room)):
                failed = True
                break
        
        if not failed:

            create_room(new_room)

            (new_x, new_y) = new_room.center()

            if(num_rooms == 0):
                player.x = new_x
                player.y = new_y
            else:

                (prev_x, prev_y) = rooms[num_rooms -1].center()

                if(randint(0,1)):

                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:

                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            
            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1

def is_blocked(x, y):
    if  my_map[x][y].blocked:
        return True
    
    for obj in objects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True
    
    return False

def message(new_msg, color = color_white):
    
    new_msg_lines = textwrap.wrap(new_msg,MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        game_msgs.append((line,color))
def render_all():
    global fov_recompute
    global visible_tiles

    if fov_recompute:
        fov_recompute = False
        visible_tiles = tdl.map.quickFOV(player.x,player.y,is_visible_tile,fov=FOV_ALGO,radius = TORCH_RADIUS,lightWalls = FOV_LIGHT_WALLS)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x,y) in visible_tiles
                wall = my_map[x][y].block_sight
                if not visible:
                    if my_map[x][y].explored:
                        if wall:
                            con.draw_char(x,y,None,fg = None,bg = color_dark_wall)
                        else:
                            con.draw_char(x,y,None, fg = None, bg = color_dark_ground)
                else:
                    if wall:
                        con.draw_char(x,y,None, fg = None, bg = color_light_wall)
                    else:
                        con.draw_char(x,y,None,fg = None, bg = color_light_ground)
                    my_map[x][y].explored = True
    
    for obj in objects:
        if obj != player:
            obj.draw()
    player.draw()

    root.blit(con,0,0,MAP_WIDTH,MAP_HEIGHT,0,0)

    panel.clear(fg = color_white, bg =color_black)

    y = 1
    for(line,color) in  game_msgs:
        panel.draw_str(MSG_X, y, line, bg = None, fg = color)
        y += 1

    render_bar(1,1,BAR_WIDTH, "HP", player.fighter.hp, player.fighter.max_hp, color_light_red, color_dark_red)
    panel.draw_str(1,0,get_names_under_mouse(), bg = None, fg = color_light_grey)

    root.blit(panel, 0, PANEL_Y, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0)

def create_h_tunnel(x1,x2,y):
    global my_map

    for x in range(min(x1,x2),max(x1,x2) +1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False

def create_v_tunnel(y1,y2,x):
    global my_map
    
    for y in range(min(y1,y2), max(y1,y2)+1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False

def get_names_under_mouse():
    global visible_tiles

    (x,y) = mouse_coord

    names = [obj.name for obj in objects if obj.x == x and obj.y == y and (obj.x, obj.y) in visible_tiles]
    names = ", ".join(names)
    return names.capitalize()

def player_move_or_attack(dx, dy):
    global fov_recompute

    x = player.x + dx
    y = player.y + dy

    target = None
    for obj in objects:
        if obj.x ==x and obj.y == y and obj.fighter:
            target = obj
            break
    
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx,dy)
        fov_recompute = True

def player_death(player):
    global game_state

    print("You died")

    game_state = "dead"

    player.char = "%"
    player.color = color_dead_char

def monster_death(monster):

    print(monster.name.capitalize() + "morreu")

    monster.char = "%"
    monster.color = color_dead_char
    monster.blocks = False
    monster.fighter = None
    monster.ai =  None
    monster.name = "restos de um " + monster.name
    monster.send_to_back()

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value)/maximum * total_width)

    panel.draw_rect(x,y, total_width, 1, None, bg = back_color)

    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg = bar_color)

    text = name + ": " + str(value) + "/" + str(maximum)
    x_centered = x + (total_width - len(text)) // 2
    panel.draw_str(x_centered, y, text, fg = (255,255,255), bg = None)

def handle_keys():
    global fov_recompute
    global game_state
    global mouse_coord

    keypress = False
    for event in  tdl.event.get():
        if event.type == "KEYDOWN":
            user_input = event
            keypress = True
        if event.type == "MOUSEMOTION":
            mouse_coord = event.cell

    if not keypress:
        return "didnt_take_a_turn"

    if user_input.key == "ENTER" and user_input.alt:
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE":
        return "exit"
    
    if game_state == "playing":
        if user_input.key == "UP":
            player_move_or_attack(0,-1)
            fov_recompute = True
        elif user_input.key == "DOWN":
            player_move_or_attack(0,1)
            fov_recompute = True
        elif user_input.key == "LEFT":
            player_move_or_attack(-1,0)
            fov_recompute = True
        elif user_input.key == "RIGHT":
            player_move_or_attack(1,0)
            fov_recompute = True
        else:
            return "didnt_take_a_turn"

tdl.set_font('arial10x10.png',greyscale = True, altLayout = True)

root = tdl.init(SCREEN_WIDTH,SCREEN_HEIGHT,title = "Roguelike",fullscreen = False)
con = tdl.Console(MAP_WIDTH,MAP_HEIGHT)
panel = tdl.Console(SCREEN_WIDTH, PANEL_HEIGHT)

fighter_component = GameObject.Fighter(hp = 30, defense = 2, power = 5,death_function= player_death)
player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, '@',"Player", (255,255,255),True,fighter = fighter_component)
game_state = "playing"
player_action = None

objects = [player]

make_map()
tdl.set_fps(LIMIT_FPS)
mouse_coord = (0,0)

message("Bem vindo ao jogo, prepare-se para o terrivel beta do meu roguelike fodaum", color = color_red)
while not tdl.event.is_window_closed():
    render_all()

    tdl.flush()
    
    for obj in objects:
        obj.clear()

    player_action = handle_keys()
    if (player_action == "exit"):
        break

    if game_state == "playing" and player_action != "didnt_take_a_turn":
        for obj in objects:
            if obj.ai:
                obj.ai.take_turn()
                
