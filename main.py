import pygame
import time
import math
from utils import scale_image, blit_rotate_center

TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.6)
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)

GRASS_BORDER = scale_image(pygame.image.load("imgs/grass_border.png"), 0.6)
GRASS_BORDER_MASK = pygame.mask.from_surface(GRASS_BORDER)

FINISH = scale_image(pygame.image.load("imgs/finish.png"), 0.13)
FINISH_POSITION = (848, 450)
FINISH_MASK = pygame.mask.from_surface(FINISH)

BLUE_CAR = scale_image(pygame.image.load("imgs/blue-car.png"), 0.33)
FREE_CAR = scale_image(pygame.image.load("imgs/free-car.png"), 0.33)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60
PATH= (858, 412), (771, 376), (590, 378), (506, 335), (427, 243), (177, 199), (98, 239), (82, 287), (95, 337), (132, 371), (189, 381), (270, 380), (356, 382), (423, 437), (475, 486), (550, 571), (545, 633), (490, 655), (403, 634), (259, 641), (210, 611), (179, 555), (141, 529), (90, 547), (80, 585), (84, 622), (134, 731), (199, 761), (628, 759), (677, 693), (712, 631), (757, 606), (811, 597), (855, 568), (876, 521), (878, 491), (411, 758)

class AbstractCar:
    IMG = BLUE_CAR
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = 1.5
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.02
        
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel
    
    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()
        
    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()
    
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        
        self.y -= vertical
        self.x -= horizontal
    
    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        
class PlayerCar(AbstractCar):
    IMG = BLUE_CAR
    START_POS = (860, 445)
    
    def reduce_speed(self, slowdown):
        self.vel = max(self.vel - self.acceleration / slowdown, 0)
        self.move()
    
    def bounce(self):
        self.vel = -self.vel
        self.move()
        
class ComputerCar(AbstractCar):
    IMG = FREE_CAR
    START_POS = (880, 445)
    
    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel
        
    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)
            
    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)
        
    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y
        
        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)
            
        if target_y > self.y:
            desired_radian_angle += math.pi
            
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360
            
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))  
        
    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1
        
    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

def draw(win, images, player_car, computer_car):
    for img, pos in images:
        win.blit(img, pos)
    
    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()
    
def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if keys[pygame.K_SPACE]:
        player_car.reduce_speed(4)
    if not moved:
        player_car.reduce_speed(2)
    

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (GRASS_BORDER, (0, 0))]
player_car = PlayerCar(8, 8)
computer_car = ComputerCar(4, 4, PATH)

while run: 
    clock.tick(FPS)
    
    draw(WIN, images, player_car, computer_car)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        
        #if event.type == pygame.MOUSEBUTTONDOWN:
            #pos = pygame.mouse.get_pos()
            #computer_car.path.append(pos)
     
    move_player(player_car)
    computer_car.move()
    
    if player_car.collide(GRASS_BORDER_MASK) != None:
        player_car.max_vel = 0.75
    else:
        player_car.max_vel = 1.5
    
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION) 
    if computer_finish_poi_collide != None:
        player_car.reset()
        computer_car.reset()
        
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 24:
            player_car.bounce()
        else:
            player_car.reset()
            computer_car.reset()
            print("finish")
        
print(computer_car.path)
pygame.quit()