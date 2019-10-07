# PyGame template.
 
# Import standard modules.
import sys
import player
import world
import math
 
# Import non-standard modules.
import pygame
import random
from pygame.locals import *

moveX = moveY = 0

# PLAYER CLASS #

class Player:
  WIDTH = 10
  HEIGHT = 10
  def __init__(self):
    self.x = 100
    self.y = 100
    self.moveX = 0
    self.moveY = 0
    self.hunger = 0
    self.hungry = False
    self.thirst = 0
    self.thirsty = False
    self.wet = False
    self.choppable = False
    self.comfort = 100
    self.health = 100
    self.rect = pygame.Rect(self.x,self.y,12,12)
    self.UPDATEINTERVAL = 0
    self.speech = []
    self.status = []
    self.noms = []
    self.closestTree = []
    self.currentChat = ""
    self.statusChat = ""
    self.talkingTime = 0
    self.SPEED = 2
    self.nomTime = 0
    self.timesRun = 0
    self.wood = 0
    self.foodbag = []
    self.water = 0
    self.leather = 0
    self.temp = 20    
    self.byFire = False
    self.underShelter = False
    self.COMBATRANGE = 60
    self.combatValid = False
    self.combatRect = self.rect
    self.combatIndex = -1
    self.inWater = False
    self.hasJacket = False
    self.targetTree = self.rect
    self.gameOver = False


  """def control(self,x,y):
    self.moveX += x
    self.moveY += y"""
  def update(self):
    if self.health <= 0 and not self.gameOver:
      self.gameOver = True
    self.UPDATEINTERVAL += 1
    
    
    if self.UPDATEINTERVAL >= 60:
      self.UPDATEINTERVAL = 0

      # temperature mechanics
      if world.locationTemp < 5:
        if self.hasJacket:
          tempChange = 1
        else:
          tempChange = 3
      elif world.locationTemp >= 5 and world.locationTemp < 15:
        if player.hasJacket:
          tempChange = 0
        else:
          tempChange = 2
      elif world.locationTemp > 20:
        tempChange = 2
      else:
        tempChange = 1
      
      if world.locationTemp < self.temp:
        self.temp -= tempChange
      else:
        self.temp += tempChange
      if self.temp < 15:
        self.comfort -= 1
      elif self.temp < 10:
        self.comfort -= 3
      elif self.temp < 5:
        self.comfort -= 5
        self.health -= 1
        if self.health <= 0:
          self.health = 0
      self.locationTemp = 10

      # hunger mechanics
      self.hunger += 2
      if self.hunger >= 100:
        self.hunger = 100
        self.health -= 2
        if self.health < 0:
          self.health = 0
      if self.hunger >= 60:
        self.hungry = True
        self.comfort -= 3
        
      elif self.hunger < 60:
        self.hungry = False

        
      # thirst mechanics
      self.thirst += 3
      if self.thirst > 100:
        self.thirst = 100
        self.health -= 4
        if self.health <= 0:
          self.health = 0
      if self.thirst >= 60:
        self.thirsty = True
        self.comfort -= 3
      if self.thirst < 60:
        self.thirsty = False


      # stepping into water
      if self.wet:
        self.comfort -= 5
        if self.comfort <= 0:
          self.health -= 1
          self.comfort = 0
      if not self.wet:
        self.comfort -= 1
        
      # am I under shelter?
      if world.shelterBuilt:
        self.underShelter = False
        if self.rect.colliderect(world.shelter):
          self.underShelter = True
          world.locationTemp = 15
          self.comfort += 2
          if self.comfort >= 100:
            self.comfort = 100

      # am I hungry?

      if self.hunger < 60:
        self.hungry = False
      
      if not self.hungry and not self.thirsty and self.underShelter:
        self.health += 2
        if self.health > 100:
          self.health = 100

      # am I near a fire?

      self.byFire = False
      tempRect = pygame.Rect(self.rect.x - 14, self.rect.y - 14, 40, 40)
      self.checkFire = tempRect.collidelist(world.fires)
      if self.checkFire > -1:
        self.byFire = True
        world.locationTemp = 20
        self.comfort += 1
        if self.comfort >= 100:
          self.comfort = 100

      if self.thirsty or self.comfort < 30 or self.wet:
        self.SPEED = 1
      else:
        self.SPEED = 2

      if self.comfort < 20:
        self.health -= 2
        if self.comfort <= 0:
          self.comfort = 0
      


  def move(self):
    self.rect.x += self.moveX
    if self.rect.x <= 0:
      self.rect.x = 0
    elif self.rect.x >= 640:
      self.rect.x = 640
    self.rect.y += self.moveY
    if self.rect.y <= 45:
      self.rect.y = 45
    elif self.rect.y >= 475:
      self.rect.y = 475

    # have I stepped over food?
    collided = self.rect.collidelist(world.foods)
    if collided >= 0 and len(self.foodbag) < 5:
      
      world.foods.pop(collided)
      self.pickUpFood()
      
    # have I stepped into water?
    feetWet = self.rect.collidelist(world.lakes)
    self.wet = False
    if feetWet >= 0:
      self.wet = True
      if "Eww, water" not in self.speech:
        self.speech.append("Eww, water")
      self.fillBottle()

    # am I close to an animal?
    closestIndex = self.closestAnimal()
    if closestIndex > -1:
      self.combatValid = True
      self.combatIndex = closestIndex
      self.combatRect = world.animals[closestIndex].rect
    else:
      self.combatValid = False

  def pickUpFood(self):
    self.foodbag.append(0)
    

  def eat(self):
    if len(self.foodbag) > 0:
      if self.hunger >= 20:
        self.foodbag.pop(0)
        self.hunger -= 30
        if self.hunger < 0:
          self.hunger = 0
      
      elif self.hunger < 20:
        if "I'm not hungry" not in self.speech:
          self.speech.append("I'm not hungry!")
    else:
      if "No food left!" not in self.speech:
        self.speech.append("No food left!")

  def fillBottle(self):
    self.water = 5

  def drank(self):
    if self.water > 0:
      
      if self.thirst >= 20:
        self.water -= 1
        self.thirst -= 30
        if self.thirst < 0:
          self.thirst = 0
      if self.thirst < 20:
        if "I'm not thirsty" not in self.speech:
          self.speech.append("I'm not thirsty!")
    else:
      if "No water" not in self.speech:
        self.speech.append("No water!")

    

  def talk(self):
    if len(self.speech) > 0:
      self.currentChat = self.speech[0]

      self.talkingTime += 1
      if self.talkingTime >= 60:
        self.talkingTime = 0
        self.speech.pop(0)
        self.currentChat = ""

  def gotWood(self): 
    
    self.choppable = False
    tempRect = pygame.Rect(self.rect.x - 14, self.rect.y - 14, 40,40)
    treeCheck = tempRect.collidelist(world.trees)
    if treeCheck != -1:
      self.choppable = True
      self.closestTree = treeCheck
      self.targetTree = world.trees[treeCheck].rect
      # print(world.trees[treeCheck].rect)

  def shelterValid(self):
    tempRect = pygame.Rect(self.rect.x - 19, self.rect.y - 19, 50,50)        
    valid = True
    if tempRect.collidelist(world.lakes) > -1:
      valid = False
    if tempRect.collidelist(world.trees) > -1:
      valid = False
    # print(valid)
    return valid

  def campfireValid(self):
    valid = True
    for lake in world.lakes:
      if player.rect.colliderect(lake):
        valid = False
    return valid

  def closestAnimal(self):
    validAnimal = False
    distToAnimal = 1000
    closestIndex = 0
    for i in range(len(world.animals)):
      # print(len(world.animals))
      tempRect = pygame.Rect(self.rect.x - (self.COMBATRANGE/2 - 5), self.rect.y - (self.COMBATRANGE/2 - 5), self.COMBATRANGE, self.COMBATRANGE)
      if tempRect.colliderect(world.animals[i]):
        validAnimal = True
        # print("Combat Valid")
        diffX = abs(tempRect.center[0] - world.animals[i].rect.center[0])
        diffY = abs(tempRect.center[1] - world.animals[i].rect.center[1])
        distance = int(math.sqrt(diffX ** 2 + diffY ** 2))
        if distance < distToAnimal:
          distToAnimal = distance
          closestIndex = i
    if validAnimal:
      # print(closestIndex)
      return closestIndex
    if not validAnimal:
      return -1


# GAME WORLD #

class World:
  def __init__(self):
    self.timeSinceNoms = 0
    self.NOMSPAWNTIME = 180
    self.temp = 10
    self.foods = []
    self.lakes = []
    self.trees = []
    self.fires = []
    self.animals = []
    self.shelterBuilt = False
    self.hour = 8
    self.time = 1
    self.locationTemp = 15
    self.date = 1
    self.season = 0 # 0 = summer, 1 = winter
    self.day = True
    self.dayselapsed = 0

    for i in range(3):
      WIDTH = random.randint(50,200)
      HEIGHT = random.randint(50,200)
      X = random.randint(50,600)
      Y = random.randint(100,450)
      self.lakes.append(pygame.Rect(X,Y,WIDTH,HEIGHT))
    while len(self.trees) < 20:
      X = random.randint(50,600)
      Y = random.randint(50,480)
      tempRect = pygame.Rect(X,Y,10,20)
      if tempRect.collidelist(self.lakes) == -1:
        self.trees.append(Tree(X,Y))
    for i in range(3):
      animalValid = False
      while not animalValid:
        X = random.randint(320,630)
        Y = random.randint(60,460)
        tempRect = pygame.Rect(X, Y, 10, 10)
        if tempRect.collidelist(self.lakes) == -1:
          self.animals.append(Animal(X,Y))
          animalValid = True

  def createShelter(self):
    self.shelter = Shelter()
    self.shelterBuilt = True

  def createFire(self):
    self.fires.append(Fire())


  def updateWorld(self):
    # print(self.locationTemp)
    self.time += 1
    if self.time >= 90:
      # print(self.hour)
      self.time = 0
      self.hour += 1
      if self.hour >= 8 and self.hour <= 20:
        self.day = True
      elif self.hour > 20 or self.hour < 8:
        self.day = False
      if self.hour > 24: # day change
        self.hour = 1
        # print("Change Day")
        self.date += 1
        self.dayselapsed += 1
        # print("Start of Day " + str(self.date))
        if self.date > 10: # season change
          self.date = 1
          self.season += 1
          # print("Change season")
          if self.season > 1:
            self.season = 0
    self.timeSinceNoms += 1
    if(self.timeSinceNoms >= 120):
      self.timeSinceNoms = 0
      if len(self.foods) < 10:
        self.foods.append(Food())
        # print(str(len(self.foods)) + " foods")
    if player.byFire:
      self.locationTemp = 21
    else:
      if player.underShelter:
        self.locationTemp = 16
      else:
        if self.day:
          if self.season == 0:
            self.locationTemp = 16
          else:
            self.locationTemp = 6
        else:
          if self.season == 0:
            self.locationTemp = 8
          else:
            self.locationTemp = -2


# FIRE CLASS #

class Fire:
  def __init__(self):
    self.x = player.rect.x
    self.y = player.rect.y
    self.rect = pygame.Rect(self.x, self.y, 10, 10)


# FOOD CLASS #

class Food:
  def __init__(self):
    # print("Food initialised")
    self.x = random.randint(0,630)
    self.y = random.randint(40,470)
    self.rect = pygame.Rect(self.x, self.y, 10,10)

# TREE CLASS

class Tree:
  def __init__(self,x,y):
    self.x = x
    self.y = y
    self.length = 20
    self.rect = pygame.Rect(x,y,10,self.length)

  def update(self):
    self.rect = pygame.Rect(self.x,(self.y + 20 - self.length),10,self.length)

# SHELTER CLASS #

class Shelter:
  def __init__(self):
    self.x = player.rect.x - 19
    self.y = player.rect.y - 19
    self.rect = pygame.Rect(self.x,self.y,50,50)

# ANIMAL CLASS

class Animal:
  def __init__(self,x,y):
    self.x = x
    self.y = y
    self.rect = pygame.Rect(self.x, self.y, 10,10)
    self.UPDATETIME = 30
    self.idle = 0
    self.ANIMALSPEED = 5
    self.hunger = 0
    self.thirst = 0
    self.SCANRANGE = 100
    self.HUNGERRANGE = 0
    self.sense = [0,0,0]
    self.health = 100
    self.dead = False

  def update(self):
    self.idle += 1   
    if self.health <= 0:
      self.health = 0
      self.dead = True
    if self.idle > self.UPDATETIME and not self.dead:
      
      self.sensePlayer()
      if self.sense[2] == 0:
        self.senseFood()
      # print(self.sense)
      self.HUNGERRANGE = int(400 * self.hunger/100)
      # print(self.HUNGERRANGE)
      self.move()
      self.idle = 0
      self.hunger += 2
      if self.hunger > 100:
        self.hunger = 100
      
    return

  def move(self):
    if self.sense [2] == 0:
      self.sense[0] = random.randint(-1,1)
      self.sense[1] = random.randint(-1,1)
      self.sense[2] = 1
    self.rect.x += self.sense[0] * self.sense[2] * self.ANIMALSPEED
    self.rect.y += self.sense[1] * self.sense[2] * self.ANIMALSPEED
    if self.rect.x >= 630:
      self.rect.x = 630
    elif self.rect.x <= 10:
      self.rect.x = 10
    elif self.rect.y >= 470:
      self.rect.y = 470
    elif self.rect.y <= 50:
      self.rect.y = 50



  def sensePlayer(self):
    self.sense = [0,0,0]
    tempRect = pygame.Rect(self.rect.x - (self.SCANRANGE/2 - 5), self.rect.y - (self.SCANRANGE/2 - 5), self.SCANRANGE, self.SCANRANGE)
    if tempRect.colliderect(player.rect):
      self.sense[2] = -1
      # print("Sensed player!")
      diffX = tempRect.x + self.SCANRANGE/2 - player.rect.x + 5
      if diffX > 0:
        # print("Sensed player to the left")
        self.sense[0] = -1
      else:
        # print("Sensed player to the right")
        self.sense[0] = 1

      diffY = tempRect.y + self.SCANRANGE/2 - player.rect.y + 5
      if diffY > 0:
        # print("Sensed player above")
        self.sense[1] = -1
      else:
        # print("Sensed player below")
        self.sense[1] = 1

  def senseFood(self):
    
    self.sense = [0,0,0]
    tempRect = pygame.Rect(self.rect.x - (self.HUNGERRANGE/2 - 5), self.rect.y - (self.HUNGERRANGE/2 - 5), self.HUNGERRANGE, self.HUNGERRANGE)
    # foodIndex = tempRect.collidelist(world.foods)
    foodIndex = self.closestFood()
    if self.hunger > 30 and foodIndex > -1:
      self.sense[2] = 1
      # print("Sensed food!")
      diffX = tempRect.x + self.HUNGERRANGE/2 - world.foods[foodIndex].x + 5
      if diffX > 0:
        self.sense[0] = -1
      else:
        self.sense[0] = 1
      diffY = tempRect.y  + self.HUNGERRANGE/2 - world.foods[foodIndex].y + 5
      if diffY > 0:
        self.sense[1] = -1
      else:
        self.sense[1] = 1
      nomRect = pygame.Rect(self.rect.x - 10, self.rect.y - 10, 30, 30)
      if nomRect.colliderect(world.foods[foodIndex]):
        world.foods.pop(foodIndex)
        # print("Ate food")
        self.hunger = 0

  def closestFood(self):
    foundFood = False
    distToFood = 1000
    closestIndex = 0
    for i in range(len(world.foods)):
      tempRect = pygame.Rect(self.rect.x - (self.HUNGERRANGE/2 - 5), self.rect.y - (self.HUNGERRANGE/2 - 5), self.HUNGERRANGE, self.HUNGERRANGE)
      if tempRect.colliderect(world.foods[i]):
        foundFood = True
        diffX = abs(tempRect.center[0] - world.foods[i].rect.center[0])
        diffY = abs(tempRect.center[1] - world.foods[i].rect.center[1])
        distance = int(math.sqrt(diffX ** 2 + diffY ** 2))
        if distance < distToFood:
          distToFood = distance
          closestIndex = i
    if foundFood:
      return closestIndex
    if not foundFood:
      return -1


# MAIN GAME #

def update(dt):
  """
  Update game. Called once per frame.
  dt is the amount of time passed since last frame.
  If you want to have constant apparent movement no matter your framerate,
  what you can do is something like
  
  x += v * dt
  
  and this will scale your velocity based on time. Extend as necessary."""
  
  # Go through events that are passed to the script by the window.

  for event in pygame.event.get():

    # We need to handle these events. Initially the only one you'll want to care
    # about is the QUIT event, because if you don't handle it, your game will crash
    # whenever someone tries to exit.
    if event.type == QUIT:
      pygame.quit() # Opposite of pygame.init
      sys.exit() # Not including this line crashes the script on Windows. Possibly
      # on other operating systems too, but I don't know for sure.
    # Handle other events as you wish.

    if event.type == KEYDOWN:
      if event.key == pygame.K_w:
        player.moveY = -player.SPEED
      if event.key == pygame.K_s:
        player.moveY = player.SPEED
      if event.key == pygame.K_a:
        player.moveX = -player.SPEED
      if event.key == pygame.K_d:
        player.moveX = player.SPEED
      if event.key == pygame.K_e:
        if player.choppable and player.wood < 5:
          if player.thirsty or player.hungry:
            if "Oof" not in player.speech:
              player.speech.append("Oof")
          else:
            if world.trees[player.closestTree].length > 1:
              world.trees[player.closestTree].length -= 1
              player.wood += 1
              player.hunger += 5
              player.thirst += 5
      if event.key == pygame.K_j:
        if not player.hasJacket:
          if player.leather >= 2:
            player.hasJacket = True
            player.leather -= 2
      if event.key == pygame.K_h:
        if player.shelterValid():          
          if not world.shelterBuilt:
            if player.wood >= 3:
              world.createShelter()
              player.wood -= 3
            else:
              if "Not enough wood" not in player.speech:
                player.speech.append("Not enough wood")
          else:
            if "Cannot build here" not in player.speech:
              player.speech.append("Cannot build here")
        else:
          if "Cannot build here" not in player.speech:
            player.speech.append("Cannot build here")
      if event.key == pygame.K_f:
        if player.campfireValid():
          if player.wood >= 1:
            world.createFire()
            player.wood -= 1
      if event.key == pygame.K_1:
        player.eat()
      if event.key == pygame.K_2:
        player.drank()
      if event.key == pygame.K_SPACE and player.combatValid:
        if player.thirst > 70 or player.hunger > 70 or player.comfort < 30:
          if "Oof" not in player.speech:
            player.speech.append("Oof")
        else:
          if not world.animals[player.combatIndex].dead:
            world.animals[player.combatIndex].health -= 20 
            player.hunger += 10
            player.thirst += 10
          else:
            player.leather += 1
            world.animals.pop(player.combatIndex)

    if event.type == KEYUP:
      if event.key == pygame.K_w:
        player.moveY = 0
      elif event.key == pygame.K_s:
        player.moveY = 0
      elif event.key == pygame.K_a:
        player.moveX = 0
      elif event.key == pygame.K_d:
        player.moveX = 0
  # Has player nommed?
  if len(player.noms) > 0:
    player.nomTime += 1
    if player.nomTime >= 60:
      player.noms.pop(0)
      player.nomTime = 0
  if not player.gameOver:
    player.talk()
    player.gotWood()
    world.updateWorld()
    player.update()
    for animal in world.animals:
      animal.update()
 
def draw(screen):
  """
  Draw things to the window. Called once per frame.
  """
  if world.hour == 7 or world.hour == 19:
    if world.season == 0:
      screen.fill(TWILIGHT) 
    else:
      screen.fill(WINTERTWI)
    # print("Twilight")
  elif world.hour > 19 or world.hour < 7:
    if world.season == 0:
    # print("Night")
      screen.fill((0,0,0))
    else:
      screen.fill(WINTERNIGHT)
  elif world.hour > 7 and world.hour < 19:
    if world.season == 0:
      screen.fill(DAYTIME)
    else:
      screen.fill(WINTERDAY)
    # print("Daytime")

  # draw water
  for lake in world.lakes:
    pygame.draw.rect(screen,BLUE,lake)
 
  # draw trees
  for tree in world.trees:
    pygame.draw.rect(screen,BROWN,tree.rect)

  # draw fires
  for fire in world.fires:
    pygame.draw.rect(screen,ORANGE,fire.rect)

  # draw player
  if player.hasJacket:
    """pygame.draw.circle(screen,WHITE,player.rect.bottomleft,3)
    pygame.draw.circle(screen,(0,0,0),player.rect.bottomleft,2)"""
    pygame.draw.circle(screen,WINTERDAY,player.rect.center,10)
  pygame.draw.circle(screen,DDGREEN, player.rect.center,7)
  pygame.draw.circle(screen,GREEN,player.rect.center,5)
  
  



  # draw 'E' next to character if they find a choppable tree near

  interactTextRect.topright = ((player.rect.x - 10), (player.rect.y + 10))
  if player.choppable:
    pygame.draw.line(screen,BROWN,player.rect.center, player.targetTree.center,2)
    screen.blit(interactText,interactTextRect)

  # draw animals
  for animal in world.animals:
    if not animal.dead:
      if animal.hunger > 30:
        pygame.draw.rect(screen,GREEN,animal.rect)
      pygame.draw.rect(screen,WHITE,animal.rect,2)
      animalHealth = font.render(str(animal.health), True, WHITE)
      animalHealthRect = animalHealth.get_rect()
      animalHealthRect.topleft = animal.rect.topright
      screen.blit(animalHealth, animalHealthRect)
    else:
      pygame.draw.rect(screen,RED,animal.rect)
    

  # screen.blit(animalHunger,animalHungerRect)

  # player talks about status
  
  # hunger circle
  if(player.hungry):
    pygame.draw.circle(screen, GREEN, player.rect.topleft, 3)

  # thirst circle
  if (player.thirsty):
    pygame.draw.circle(screen, LBLUE, player.rect.topright, 3)

  # draw combat circle
  if player.combatValid:
    pygame.draw.circle(screen, RED, player.rect.bottomright,3)
    pygame.draw.line(screen, RED, player.rect.center, player.combatRect.center, 2)

  # draw player speech
  chat = font.render(player.currentChat, True, WHITE)
  chatRect = chat.get_rect()
  chatRect.topleft = ((player.rect.x + 15), (player.rect.y - 13))
  screen.blit(chat,chatRect)

  # grey background for bars

  pygame.draw.rect(screen, (130,130,130), pygame.Rect(0,0,640,40))

  # draw health bar
  pygame.draw.rect(screen,RED,pygame.Rect(10,10,player.health,BARHEIGHT))
  pygame.draw.rect(screen,RED,pygame.Rect(10,10,100,20),2)
  screen.blit(healthText, healthTextRect)

  # draw hunger bar
  pygame.draw.rect(screen,GREEN, pygame.Rect(130,10,player.hunger, BARHEIGHT))
  pygame.draw.rect(screen,GREEN,pygame.Rect(130,10,100,20),2)
  screen.blit(hungerText, hungerTextRect)

  # draw thirst bar
  pygame.draw.rect(screen, BLUE, pygame.Rect(250,10,player.thirst, BARHEIGHT))
  pygame.draw.rect(screen, BLUE, pygame.Rect(250,10,100,20),2)
  screen.blit(thirstText, thirstTextRect)

  """# draw temperature
  if player.underShelter:
    pygame.draw.rect(screen, DGREEN, pygame.Rect(563,5,40,28))
  tempDisplay = str(player.temp) + "C"
  if player.temp < 16:
    temp = font.render(tempDisplay, True, BLUE)
  elif player.temp < 21:
    temp = font.render(tempDisplay, True, GREEN)
  elif player.temp < 31:
    temp = font.render(tempDisplay, True, ORANGE)
  elif player.temp < 41:
    temp = font.render(tempDisplay, True, RED)  
  tempRect = temp.get_rect()
  tempRect.topleft = (570, 10)
  screen.blit(temp, tempRect)
  if player.byFire:
    pygame.draw.rect(screen, ORANGE, pygame.Rect(563, 5, 40, 28), 2)"""

  # draw temperature bar

  pygame.draw.rect(screen,COLDBLUE,pygame.Rect(455,8,24,20))
  pygame.draw.rect(screen,BLUE,pygame.Rect(479,8,40,20))
  pygame.draw.rect(screen,GREEN,pygame.Rect(519,8,64,20))
  tempLine = player.temp * 4
  pygame.draw.line(screen,RED,(455+tempLine,8), (455+tempLine,28),2)
  pygame.draw.rect(screen,WHITE,pygame.Rect(455,8,128,20),2)

  # comfort status
  if(player.comfort >= 50):
    comfortness = "Good (" + str(player.comfort) + ")"
    comfortText = font.render(comfortness, True, GREEN)
  elif (player.comfort >= 30):
    comfortness = "Okay (" + str(player.comfort) + ")"
    comfortText = font.render(comfortness, True, ORANGE)
  else:
    comfortness = "Terrible (" + str(player.comfort) + ")"
    comfortText = font.render(comfortness, True, RED)
  comfortTextRect = comfortText.get_rect()
  comfortTextRect.topleft = (370,10)
  screen.blit(comfortText,comfortTextRect)

  # draw wood amount
  for i in range(player.wood):
    pygame.draw.rect(screen,BROWN,pygame.Rect(18 * i + 10, 68, 10, 10))

  # draw foods
  for food in world.foods:
    pygame.draw.rect(screen,GREEN, food.rect)
    pygame.draw.rect(screen,BROWN, food.rect,2)
  
  # draw Noms
  for nom in player.noms:
    nomText = font.render("Nom", True, GREEN)
    screen.blit(nomText,nom)

  # draw shelter
  if world.shelterBuilt:
    pygame.draw.rect(screen,BROWN,world.shelter.rect,3)

  # draw food bag items
  for i in range(len(player.foodbag)):
    pygame.draw.rect(screen,GREEN, pygame.Rect(18 * i + 10, 53, 10,10))

  # draw water items
  for i in range(player.water):
    pygame.draw.rect(screen,BLUE,pygame.Rect(18 * i + 10, 83, 10, 10))

  # draw leather items
  for i in range(player.leather):
    pygame.draw.rect(screen, ORANGE, pygame.Rect(18 * i + 10, 98, 10, 10), 2)

  # Display time
  timeStr = str(world.hour) + ".00"
  timeText = font.render(timeStr, True, WHITE)
  timeTextRect = timeText.get_rect()
  timeTextRect.topleft = (570, 40)
  screen.blit(timeText, timeTextRect)

  # display season 

  if world.season == 0:
    pygame.draw.rect(screen,ORANGE, pygame.Rect(495, 38, 67, 22))
    screen.blit(summerText, summerTextRect)
  else:
    pygame.draw.rect(screen,WHITE, pygame.Rect(495, 38, 67, 22))
    screen.blit(winterText,winterTextRect)

  # draw Game Over

  if player.gameOver:
    pygame.draw.rect(screen,(0,0,0), pygame.Rect(45, 190, 550, 100))
    pygame.draw.rect(screen,WHITE,pygame.Rect(45,190,550,100),2)
    gameOverText = bigfont.render("Game Over, Days Survived = " + str(world.dayselapsed), True, RED)
    gameOverTextRect = gameOverText.get_rect()
    gameOverTextRect.center = (320,215)
    screen.blit(gameOverText,gameOverTextRect)

    quitText = bigfont.render("Close the game and restart to try again!", True, RED)
    quitTextRect = quitText.get_rect()
    quitTextRect.center = (320,255)
    screen.blit(quitText,quitTextRect)

  # Redraw screen here.
  
  # Flip the display so that the things we drew actually show up.
  pygame.display.flip()
 
def runPyGame():
  # Initialise PyGame.
  pygame.init()
  
  # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
  fps = 60.0
  fpsClock = pygame.time.Clock()
  
  # Set up the window.
  width, height = 640, 480
  screen = pygame.display.set_mode((width, height))
  
  # screen is the surface representing the window.
  # PyGame surfaces can be thought of as screen sections that you can draw onto.
  # You can also draw surfaces onto other surfaces, rotate surfaces, and transform surfaces.
  
  # Main game loop.
  dt = 1/fps # dt is the time since last frame.
  while True: # Loop forever!
    if not player.gameOver:
      player.move()
      
    
      for tree in world.trees:
        tree.update()
    update(dt) # You can update/draw here, I've just moved the code for neatness.
    draw(screen)

    
    dt = fpsClock.tick(fps)

WIDTH = 20
HEIGHT = 20

RED = (255,0,0)
GREEN = (0,200,0)
DGREEN = (0,160,0)
DDGREEN = (0,30,0)
DAYTIME = (165,124,24)
TWILIGHT = (82,62,12)
BLUE =  (0,0,255)
LBLUE = (20,20,255)
COLDBLUE = (120,120,255)
WHITE = (255,255,255)
WINTERDAY = (200,200,220)
WINTERNIGHT = (30,30,30)
WINTERTWI = (70,70,70)
BROWN = (165,42,42)
ORANGE = (255,165,0)
BARHEIGHT = 20
PLAYERUPDATEINTERVAL = 60
world = World()
# print(world.trees)
player = Player()
animals = []

# create animals


pygame.font.init()
font = pygame.font.Font('resources/arialbd.ttf',15)
bigfont = pygame.font.Font('resources/arialbd.ttf',27)

healthText = font.render("Health", True, WHITE)
healthTextRect = healthText.get_rect()
healthTextRect.topleft = (40,10)

hungerText = font.render("Hunger", True, WHITE)
hungerTextRect = hungerText.get_rect()
hungerTextRect.topleft = (150,10)

thirstText = font.render("Thirst", True, WHITE)
thirstTextRect = thirstText.get_rect()
thirstTextRect.topleft = (280,10)

interactText = font.render("E", True, WHITE)
interactTextRect = interactText.get_rect()

winterText = font.render("Winter", True, (0,0,0))
winterTextRect = winterText.get_rect()
winterTextRect.topleft = (500,40)

summerText = font.render("Summer", True, DGREEN)
summerTextRect = summerText.get_rect()
summerTextRect.topleft = (500,40)



runPyGame()
