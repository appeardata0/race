from typing import Any
import pygame
import time
import math

def scale_image(img,factor):
    size = round(img.get_width() * factor),round(img.get_height() * factor)
    return pygame.transform.scale(img,size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    win.blit(rotated_image, new_rect.topleft)

GRASS = scale_image(pygame.image.load("Imgs/grass.png"),1.5)
TRACK = scale_image(pygame.image.load("Imgs/Track.png"),0.4)
TRACK_BORDER = scale_image(pygame.image.load("Imgs/Track_border.png"),0.4)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = scale_image(pygame.image.load("Imgs/finish.png"),1.5)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (100,260)
RED_CAR = scale_image(pygame.image.load("Imgs/Car_red.png"),0.50)
GREEN_CAR = scale_image(pygame.image.load("Imgs/Car_green.png"),0.50)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("CAR GAME")

FPS = 60
PATH = [(158, 137), (153, 112), (140, 97), (127, 97), (115, 97), (100, 102), (84, 347), (249, 536), (261, 541), (268, 544), (279, 545), (291, 545), (299, 542), (307, 539), (314, 527), (328, 401), (333, 393), (338, 391), (344, 388), (350, 385), (356, 382), (364, 380), (374, 379), (384, 378), (396, 377), (411, 377), (420, 378), (424, 383), (432, 389), (439, 398), (444, 407), (468, 531), (480, 539), (487, 539), (500, 539), (517, 539), (529, 537), (548, 536), (565, 339), (556, 320), (542, 311), (534, 298), (519, 295), (336, 290), (326, 270), (322, 252), (325, 237), (333, 228), (533, 218), (510, 225), (523, 221), (546, 212), (548, 199), (549, 123), (544, 114), (540, 108), (536, 104), (524, 101), (274, 97), (260, 96), (248, 102), (245, 113), (248, 123), (228, 297), (222, 312), (208, 322), (185, 318), (173, 297)]
class Abstractcar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.accelaration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel 
        elif right:
            self.angle -= self.rotation_vel 

    def draw(self, win):
        blit_rotate_center(win, self.img,(self.x,self.y),self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.accelaration, self.max_vel)
        self.move()
    def move_backward(self):
        self.vel = max(self.vel - self.accelaration, -self.max_vel/2)
        self.move()
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x),int(self.y - y))
        poi = mask.overlap(car_mask,offset)
        return poi
    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class Playercar(Abstractcar):
    IMG = RED_CAR
    START_POS = (145,200)
    def reduce_speed(self):
        self.vel = max(self.vel - self.accelaration / 2,0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
class Computercar(Abstractcar):
    IMG = GREEN_CAR
    START_POS = (145, 150)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win,(255,0,0),point, 5)

    def draw(self,win):
        super().draw(win)
        #self.draw_points(win)

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
        rect = pygame.Rect(self.x , self.y , self.img.get_width() , self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

def draw(win,images,player_car,computer_car):
    for img,pos in images:
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
    if not moved:
        player_car.reduce_speed()


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)),(TRACK,(0, 0)),(FINISH,FINISH_POSITION),(TRACK_BORDER,(0,0))]
player_car = Playercar(5,5)
computer_car = Computercar(5,5,PATH)

while run:
    clock.tick(FPS)
    draw(WIN, images,player_car,computer_car)
    WIN.blit(GRASS, (0,0))
    WIN.blit(TRACK, (0,0))
    WIN.blit(RED_CAR, (0,0))
    

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)
    computer_car.move()

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, * FINISH_POSITION)
    if computer_finish_poi_collide != None:
        player_car.reset()
        computer_car.reset() 
    Player_finish_poi_collide = player_car.collide(FINISH_MASK, * FINISH_POSITION)    
    if Player_finish_poi_collide !=None:
        if Player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            player_car.reset()
            computer_car.reset() 

print(computer_car.path)
  
pygame.quit()