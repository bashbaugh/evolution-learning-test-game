# Evolution learning game 1
# By Benjamin A.
# https://github.com/scitronboy/evolution-learning-test-game

import pygame
import random
from operator import attrgetter
from time import sleep

manual_control = False
speedup = 0

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
            self.deltatime = self.clock.tick(50) + speedup
            self.bs.update()
            if self.E.alive:
                self.E.update()
            
            pygame.display.flip()
            
        print("game aborted")
        pygame.quit()
        
class BlockSpawner:
    mindist = 60
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
    speeddenom = 6
    speedmultipdenom = 300
    minheight = 10
    maxheight = 30
    minwidth = 10
    maxwidth = 20
    multipmax = 3
    def __init__(self, game):
        self.game = game
        #self.active = True
        w = random.randint(self.minwidth, self.maxwidth)
        h = random.randint(self.minheight, self.maxheight)
        self.rect = pygame.Rect(640, 160 - h, w, h)
        
    def update(self):
        multiplier = (self.game.E.score / self.speedmultipdenom) + 1
        if multiplier > self.multipmax:
            multiplier = self.multipmax
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
        jsd = self.jumpspeeddenom + (((self.game.E.score / self.game.bs.blocks[0].speedmultipdenom) + 1) * self.jsdmultipfactor)
        jumpquant = self.game.deltatime / jsd
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
        self.jsdmultipfactor = 0
        self.playerID = 0
    
    def update(self):
        for e in self.game.events:
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE) and (self.direction == 0):
                self.direction = 1
        super().update()
        
class EvolvedPlayer(Player):
    def __init__(self, game, ID, jumpatdist, jadtolerance, jumpheight, jumpspeeddenom, jsdmultipfactor):
        self.jumpatdist = jumpatdist
        self.jadtolerance = jadtolerance
        self.jsdmultipfactor = jsdmultipfactor
        self.playerID = ID
        super().__init__(game, jumpspeeddenom, jumpheight)
    
    def update(self):
        for block in self.game.bs.blocks:
            if (block.rect.centerx > Player.defaultx + self.jumpatdist - (self.jadtolerance / 2)) and (block.rect.centerx < Player.defaultx + self.jumpatdist + (self.jadtolerance / 2)) and self.direction == 0:
                self.direction = 1
        super().update()
        
    def die(self):
        super().die()
        print("jumpatdist: {0}\njadtolerance: {1}\njumpheight: {2}\njumpspeeddenom: {3}\njsdmultipfactor: {4}\n".format(self.jumpatdist, self.jadtolerance, self.jumpheight, self.jumpspeeddenom, self.jsdmultipfactor))
        if self.score > self.game.E.goalscore:
            print("PLAYER {} HAS REACHED GOAL SCORE, EVOLUTION ENDED\n".format(self.playerID))
            self.game.E.alive = False
        
class EvolutionV1:
    numplayers = 6
    numparents = 3
    keepparents = False
    maxgenerations = 300 
    goalscore = 2000
    #improvementavgsamples = 2
    improvementlookback = 4
    reinitstagnancethreshhold = 20
    reinitquant = 2
    
    maxmutation = 25
    maxjsdmutation = 1
    maxjsdmfmutation = 2
    minjumpatdist = 0
    maxjumpatdist = 200
    minjadtolerance = 0
    maxjadtolerance = 70
    minjumpheight = 1
    maxjumpheight = 120
    minjumpspeeddenom = 1
    maxjumpspeeddenom = 7
    minjsdmultipfactor = -7
    maxjsdmultipfactor = 7
    
    
    
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
        self.bestscores = []
        self.justreinit = True
        self.score = 0
    
    def update(self):
        for i, player in enumerate(self.players):
            if player.alive:
                player.update()
            else:
                self.deadplayers.append(self.players.pop(i))

        if len(self.players) == 0:
            self.bestscores.append(self.deadplayers[-1].score)
            print("Generation Dead")
            self.breed()
        try:
            self.score = self.players[0].score
        except:
            self.score = 1
        
        numptext = self.game.font.render(str(len(self.players)), True, green)
        gentext = self.game.font.render("G" + str(self.generation), True, green)
        lastscoretext = self.game.font.render("last bests: {}".format(str(self.bestscores[-4:])), True, green)
        ritext = self.game.font.render("REINIT", True, green)
        multiptext = self.game.font.render("{}%".format(str(int(((self.score / Block.speedmultipdenom)) / (Block.multipmax - 1)* 100))), True, green)
        
        self.game.screen.blit(numptext, (600, 10))
        self.game.screen.blit(gentext, (500, 10))
        self.game.screen.blit(lastscoretext, (100, 10))
        self.game.screen.blit(multiptext, (50, 10))
        if self.justreinit:
            self.game.screen.blit(ritext, (400, 10))
            
    def init(self, numplayers):
        for i in range(numplayers):
            jumpatdist = random.randint(self.minjumpatdist, self.maxjumpatdist)
            jadtolerance = random.randint(self.minjadtolerance, self.maxjadtolerance)
            jumpheight = random.randint(self.minjumpheight, self.maxjumpheight)
            jumpspeeddenom = random.randint(self.minjumpspeeddenom, self.maxjumpspeeddenom)
            jsdmultipfactor = random.uniform(self.minjsdmultipfactor, self.maxjsdmultipfactor)
            self.players.append(EvolvedPlayer(self.game, self.nextid, jumpatdist, jadtolerance, jumpheight, jumpspeeddenom, jsdmultipfactor))
            self.nextid += 1
            
    def breed(self):
        def crossovermutate():
            assert len(self.deadplayers) == self.numparents
            #self.deadplayers.sort(key=attrgetter('score'))
            for i in range(len(self.deadplayers) - 1):
                for j in range(len(self.deadplayers) - i - 1):
                    crossoverpoint = random.randint(1,4)
                    p1 = self.deadplayers[-(i + 1)]
                    p2 = self.deadplayers[-(i + j + 1)]
                    parent1 = [p1.jumpatdist, p1.jadtolerance, p1.jumpheight, p1.jumpspeeddenom, p1.jsdmultipfactor]
                    parent2 = [p2.jumpatdist, p2.jadtolerance, p2.jumpheight, p2.jumpspeeddenom, p2.jsdmultipfactor]
                    offspring = parent1[:crossoverpoint] + parent2[crossoverpoint:]
                    paramtomutate = random.randint(0,4)
                    if paramtomutate == 3:
                        offspring[paramtomutate] += random.randint(-self.maxjsdmutation, self.maxjsdmutation)
                    elif paramtomutate == 4:
                        offspring[paramtomutate] += random.uniform(-self.maxjsdmfmutation, self.maxjsdmfmutation)
                    else:
                        offspring[paramtomutate] += random.randint(-self.maxmutation, self.maxmutation)
                    print("param {} mutated".format(paramtomutate))
                    self.players.append(EvolvedPlayer(self.game, self.nextid, offspring[0], offspring[1], offspring[2], offspring[3], offspring[4]))
                    self.nextid += 1
        self.generation += 1
        print("\n---------Generation {}----------".format(self.generation))
        if self.generation >= self.maxgenerations:
            self.alive = False
            print("\nEARLY STOP: MAX GENERATIONS REACHED")
            return
        del self.deadplayers[:-self.numparents]            
        if len(self.bestscores) >= self.improvementlookback + 1:
            bestavg = (self.bestscores[-1] + self.bestscores[-2]) / 2
            lookbackavg = (self.bestscores[-self.improvementlookback] + self.bestscores[-(self.improvementlookback + 1)]) / 2
            if bestavg - lookbackavg < self.reinitstagnancethreshhold:
                print("Stagnance detected: initializing {} new players".format(self.reinitquant))
                self.init(self.reinitquant)
                self.justreinit = True
            else:
                self.justreinit = False
        else:
            self.justreinit = False
                
        crossovermutate()
            
        if self.keepparents:
            for p in self.deadplayers:
                p.alive = True
                p.rawscore = 0
                p.direction = -1
                self.players.append(p)
        else:
            crossovermutate()

        self.deadplayers = []
        self.game.bs.blocks = []
        self.game.bs.spawn = True
        print("Offspring generated, running game\n")
            
            
            

    
game = Game()
