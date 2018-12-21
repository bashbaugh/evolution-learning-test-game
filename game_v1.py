import pygame
import random
from operator import attrgetter
from time import sleep

manual_control = False

black = (0,0,0)
red = (255,0,0)
green = (0,255,0)

class Game:
    def __init__(self):
        print("Initializing game")
        pygame.init()
        self.screen = pygame.display.set_mode((640, 160))
        pygame.display.set_caption("Evolution Learning Game")
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.deltatime = 0
        self.done = False
        self.events = None
        self.font = pygame.font.SysFont("comicsansms", 24)
        
        self.bs = BlockSpawner(self)
        if manual_control:
            self.E = ManualPlayer(self)
        else:
            self.E = EvolutionV1(self)
        
        self.rungame()
        
    def rungame(self):
        print("running game")
        while not self.done:
            self.events = pygame.event.get()
            for e in self.events:
                if (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE) or (e.type == pygame.QUIT):
                    self.done = True
            self.screen.fill((255, 255, 255))
            self.deltatime = self.clock.tick(50)
            self.bs.update()
            if self.E.alive:
                self.E.update()
            
            pygame.display.flip()
            
        print("game aborted")
        pygame.quit()
        
class BlockSpawner:
    mindist = 50
    maxdist = 250
    def __init__(self, game):
        self.game = game
        self.blocks = []
        self.spawn = True
        self.nextblockdist = None
        
    def update(self):
        if self.spawn:
            self.spawn = False
            self.blocks.append(Block(self.game))
            self.nextblockdist = random.randint(self.mindist, self.maxdist)
            
        if self.blocks[-1].rect.centerx <= 640 - self.nextblockdist:
            self.spawn = True
            
        if self.blocks[0].rect.centerx < -10:
            del self.blocks[0]
        
        for block in self.blocks:
            block.update()
        
            


class Block:
    startspeeddenom = 6
    speedmultipdenom = 60
    speeddenommin = 1
    def __init__(self, game):
        self.game = game
        self.speeddenom = self.startspeeddenom
        #self.active = True
        self.rect = pygame.Rect(640, 145, 15, 15)
        
    def update(self):
        multiplier = int(self.game.E.score / self.speedmultipdenom) + 1
        if multiplier < self.speeddenommin:
            multiplier = self.speeddenommin
        movequant = (self.game.deltatime / self.speeddenom) * multiplier
        
        self.rect.move_ip(-movequant, 0)
        pygame.draw.rect(self.game.screen, red, self.rect)
        
        
        
class Player:
    defaultheight = 150
    defaultx = 20
    r = 8 # radius
    scoredenom = 100
    
    def __init__(self, game, jumpspeeddenom, jumpheight):
        self.alive = True
        self.game = game
        #self.height = self.defaultheight
        self.direction = 0
        self.rect = pygame.Rect(self.defaultx, self.defaultheight - int(self.r / 2), self.r, self.r)
        self.jumpspeeddenom = jumpspeeddenom
        self.jumpheight = jumpheight
        self.score = 0
        self.rawscore = 0
        
    def update(self):
        self.rawscore += int(self.game.deltatime / self.game.bs.blocks[0].speeddenom)
        self.score = int(self.rawscore / self.scoredenom)
        jumpquant = self.game.deltatime / self.jumpspeeddenom
        self.rect.move_ip(0, jumpquant * self.direction * -1)
        if self.rect.centery <= self.defaultheight - self.jumpheight:
            self.direction = -1
        if self.rect.centery >= self.defaultheight:
            self.direction = 0
            self.rect.centery = self.defaultheight
        pygame.draw.circle(self.game.screen, black, self.rect.center, self.r)
        for block in self.game.bs.blocks:
            if self.rect.colliderect(block.rect):
                self.die()
        scoretext = self.game.font.render(str(self.score), True, green)
        self.game.screen.blit(scoretext, (10, 10))
    
    def die(self):
        self.alive = False
        print("PLAYER {} died at score {}".format(self.playerID, self.score))
        
class ManualPlayer(Player):
    jumpspeeddenom = 5
    jumpheight = 60
    def __init__(self, game):
        super().__init__(game, self.jumpspeeddenom, self.jumpheight)
        self.playerID = 0
    
    def update(self):
        for e in self.game.events:
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE) and (self.direction == 0):
                self.direction = 1
        super().update()
        
class EvolvedPlayer(Player):
    def __init__(self, game, ID, jumpatdist, jadtolerance, jumpheight, jumpspeeddenom):
        self.jumpatdist = jumpatdist
        self.jadtolerance = jadtolerance
        self.playerID = ID
        super().__init__(game, jumpspeeddenom, jumpheight)
    
    def update(self):
        for block in self.game.bs.blocks:
            if (block.rect.centerx > Player.defaultx + self.jumpatdist - (self.jadtolerance / 2)) and (block.rect.centerx < Player.defaultx + self.jumpatdist + (self.jadtolerance / 2)) and self.direction == 0:
                self.direction = 1
        super().update()
        
    def die(self):
        super().die()
        print("jumpatdist: {0}\njadtolerance: {1}\njumpheight: {2}\njumpspeeddenom: {3}\n".format(self.jumpatdist, self.jadtolerance, self.jumpheight, self.jumpspeeddenom))
        if self.score > self.game.E.goalscore:
            print("PLAYER {} HAS REACHED GOAL SCORE, EVOLUTION ENDED\n".format(self.playerID))
            self.game.E.alive = False
        
class EvolutionV1:
    numplayers = 6
    numparents = 3
    maxgenerations = 15
    goalscore = 150
    maxmutation = 10
    minjumpatdist = 0
    maxjumpatdist = 200
    minjadtolerance = 0
    maxjadtolerance = 70
    minjumpheight = 1
    maxjumpheight = 150
    minjumpspeeddenom = 1
    maxjumpspeeddenom = 12
    maxjsdmutation = 1
    
    def __init__(self, game):
        self.game = game
        self.alive = True
        self.generation = 0
        self.players = []
        self.deadplayers = []
        self.nextid = 0
        print("\n---------Generation 0----------")
        #sleep(1)
        self.init(self.numplayers)
        self.score = 0
    
    def update(self):
        for i, player in enumerate(self.players):
            if player.alive:
                player.update()
            else:
                self.deadplayers.append(self.players.pop(i))

        if len(self.players) == 0:
            print("Generation Dead")
            self.breed()
        try:
            self.score = self.players[0].score
        except:
            self.score = 1
        
        numptext = self.game.font.render(str(len(self.players)), True, green)
        self.game.screen.blit(numptext, (600, 10))
            
    def init(self, numplayers):
        for i in range(numplayers):
            jumpatdist = random.randint(self.minjumpatdist, self.maxjumpatdist)
            jadtolerance = random.randint(self.minjadtolerance, self.maxjadtolerance)
            jumpheight = random.randint(self.minjumpheight, self.maxjumpheight)
            jumpspeeddenom = random.randint(self.minjumpspeeddenom, self.maxjumpspeeddenom)
            self.players.append(EvolvedPlayer(self.game, self.nextid, jumpatdist, jadtolerance, jumpheight, jumpspeeddenom))
            self.nextid += 1
            
    def breed(self):
        self.generation += 1
        print("\n---------Generation {}----------".format(self.generation))
        if self.generation >= self.maxgenerations:
            self.alive = False
            print("\nEARLY STOP: MAX GENERATIONS REACHED")
            return
        #sleep(2)
        assert self.players == []
        del self.deadplayers[:self.numparents]
        self.deadplayers.sort(key=attrgetter('score'))
        for i in range(len(self.deadplayers) - 1):
            for j in range(len(self.deadplayers) - i - 1):
                crossoverpoint = random.randint(1,3)
                p1 = self.deadplayers[i]
                p2 = self.deadplayers[i + j]
                parent1 = [p1.jumpatdist, p1.jadtolerance, p1.jumpheight, p1.jumpspeeddenom]
                parent2 = [p2.jumpatdist, p2.jadtolerance, p2.jumpheight, p2.jumpspeeddenom]
                offspring = parent1[:crossoverpoint] + parent2[crossoverpoint:]
                paramtomutate = random.randint(0,3)
                if paramtomutate == 3:
                    offspring[paramtomutate] += random.randint(-self.maxjsdmutation, self.maxjsdmutation)
                else:
                    offspring[paramtomutate] += random.randint(-self.maxmutation, self.maxmutation)
                self.players.append(EvolvedPlayer(self.game, self.nextid, offspring[0], offspring[1], offspring[2], offspring[3]))
                self.nextid += 1
        if random.randint(0,1):
            self.init(1)
        for p in self.deadplayers:
            p.alive = True
            p.rawscore = 0
            p.direction = -1
            self.players.append(p)

        self.deadplayers = []
        self.game.bs.blocks = []
        self.game.bs.spawn = True
        print("Offspring generated, running game\n")
            
            
            

    
game = Game()
    
