import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center

pygame.font.init()

TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.6)
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)

GRASS_BORDER = scale_image(pygame.image.load("imgs/grass_border.png"), 0.6)
GRASS_BORDER_MASK = pygame.mask.from_surface(GRASS_BORDER)

FINISH = scale_image(pygame.image.load("imgs/finish.png"), 0.13)
FINISH_POSITION = (848, 450)
FINISH_MASK = pygame.mask.from_surface(FINISH)

COIN1 = scale_image(pygame.image.load("imgs/coins.png"), 0.03)
COIN1_MASK = pygame.mask.from_surface(COIN1)
PATH_COIN = ((416, 223), (187, 379), (534, 554), (174, 530), (715, 619))
# COIN1_POSITION = (416, 223)
# COIN2 = scale_image(pygame.image.load("imgs/coins.png"), 0.03)
# COIN2_MASK = pygame.mask.from_surface(COIN1)
# COIN2_POSITION = (187, 379)
# COIN3 = scale_image(pygame.image.load("imgs/coins.png"), 0.03)
# COIN3_MASK = pygame.mask.from_surface(COIN1)
# COIN3_POSITION = (534, 554)
# COIN4 = scale_image(pygame.image.load("imgs/coins.png"), 0.03)
# COIN4_MASK = pygame.mask.from_surface(COIN1)
# COIN4_POSITION = (174, 530)
# COIN5 = scale_image(pygame.image.load("imgs/coins.png"), 0.03)
# COIN5_MASK = pygame.mask.from_surface(COIN1)
# COIN5_POSITION = (715, 619)


BLUE_CAR = scale_image(pygame.image.load("imgs/blue-car.png"), 0.33)
FREE_CAR = scale_image(pygame.image.load("imgs/free-car.png"), 0.33)
POLICE_CAR = scale_image(pygame.image.load("imgs/police.png"), 0.18)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
PATH = (600, 363), (416, 223), (145, 195), (187, 379), (358, 383), (534, 554), (422, 633), (264, 642), (174, 530), (
    120, 711), (600, 755), (715, 619), (848, 573), (864, 399)


class GameInfo:
    LAPS = 3

    def __init__(self, lap=1):
        self.lap = lap
        self.started = False
        self.lap_start_time = 0

    def next_lap(self):
        self.lap += 1
        self.started = False

    def reset(self):
        self.lap = 1
        self.started = False
        self.lap_start_time = 0

    def game_finished(self):
        return self.lap > self.LAPS

    def start_lap(self):
        self.started = True
        self.lap_start_time = time.time()

    def get_lap_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.lap_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
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
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
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

    def increase_speed(self):
        self.max_vel = 2.5
        if self.collide(GRASS_BORDER_MASK) != None:
          self.max_vel = 1

    def return_max_speed(self):
        self.max_vel = 1.5
        if self.collide(GRASS_BORDER_MASK) != None:
          self.max_vel = 0.75
        else:
          self.max_vel = 1.5
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
        # self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

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
        
    def next_lap(self, lap):
        self.reset()
        self.vel = self.max_vel + (lap - 1) * 0.02
        self.current_point = 0

class Coins:
    IMG = COIN1

    def __init__(self, x, y):
        self.img = self.IMG
        self.x, self.y = (x, y)
        self.passed = False
        self.mask = COIN1_MASK







class PoliceCar(AbstractCar):
    IMG = POLICE_CAR
    START_POS = (350, 120)

def draw(win, images, player_car, computer_car, police_car, game_info):
    for img, pos in images:
        win.blit(img, pos)
        
    lap_text = MAIN_FONT.render(f"Lap {game_info.lap}", 1, (255, 255, 255))
    win.blit(lap_text, (10, HEIGHT - lap_text.get_height() - 80))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_lap_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 0))


    player_car.draw(win)
    computer_car.draw(win)
    police_car.draw(win)
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
        if keys[pygame.K_SPACE]:
            player_car.increase_speed()
        else:
            player_car.return_max_speed()
        player_car.move_forward()
    else:
        if player_car.collide(GRASS_BORDER_MASK) != None:
          player_car.max_vel = 0.75
        else:
          player_car.max_vel = 1.5
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if not moved:
        player_car.reduce_speed(2)

def coin_collision(player_car):
    player_coin1_collide = player_car.collide(COIN1_MASK, *PATH_COIN[0])
    player_coin2_collide = player_car.collide(COIN1_MASK, *PATH_COIN[1])
    player_coin3_collide = player_car.collide(COIN1_MASK, *PATH_COIN[2])
    player_coin4_collide = player_car.collide(COIN1_MASK, *PATH_COIN[3])
    player_coin5_collide = player_car.collide(COIN1_MASK, *PATH_COIN[4])
    if player_coin1_collide != None:
        coin1.passed = True
        print(coin1.passed)
        print('1-ok')
        # монетка пропадает
    if player_coin2_collide != None:
        coin2.passed = True
        print(coin2.passed)
        print('2-ok')
        # монетка пропадает
    if player_coin3_collide != None:
        coin3.passed = True
        print(coin3.passed)
        print('3-ok')
        # монетка пропадает
    if player_coin4_collide != None:
        coin4.passed = True
        print(coin4.passed)
        print('4-ok')
        # монетка пропадает
    if player_coin5_collide != None:
        coin5.passed = True
        print(coin5.passed)
        print('5-ok')
        # монетка пропадает




def handle_collision(player_car, computer_car, game_info):
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        blit_text_center(WIN, MAIN_FONT, "You lose!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 24:
            player_car.bounce()
        else:
            game_info.next_lap()
            player_car.reset()
            computer_car.next_lap(game_info.lap)
            #print("finish")


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION),(COIN1, PATH_COIN[0]), (COIN1, PATH_COIN[1]), (COIN1, PATH_COIN[2]), (COIN1, PATH_COIN[3]), (COIN1, PATH_COIN[4]), (GRASS_BORDER, (0, 0)), ]
# (COIN3, COIN3_POSITION),(COIN4, COIN4_POSITION),(COIN5, COIN5_POSITION)
player_car = PlayerCar(8, 8)
computer_car = ComputerCar(1.4, 1.4, PATH)
police_car = PoliceCar(1.5, 1.5)
game_info = GameInfo()

# (600, 363), (416, 223), (145, 195), (187, 379), (358, 383), (534, 554), (422, 633), (264, 642), (174, 530), (
#     120, 711), (600, 755), (715, 619), (848, 573), (864, 399)

coin1 = Coins(416, 223)
coin2 = Coins(187, 379)
coin3 = Coins(534, 554)
coin4 = Coins(174, 530)
coin5 = Coins(715, 619)

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car, police_car, game_info)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start race {game_info.lap}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_lap()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        #if event.type == pygame.MOUSEBUTTONDOWN:
            #pos = pygame.mouse.get_pos()
            #computer_car.path.append(pos)

    move_player(player_car)
    computer_car.move()

    coin_collision(player_car)

    handle_collision(player_car, computer_car, game_info)
    
    if game_info.game_finished():        
        blit_text_center(WIN, MAIN_FONT, "WIN!")
        pygame.time.wait(5000)
        pygame.display.update()
        game_info.reset()
        player_car.reset()
        computer_car.reset()
        
#print(computer_car.path)
pygame.quit()
