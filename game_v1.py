import pygame
import random

manual_control = True

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
        self.players = []
        if manual_control:
            self.players.append(ManualPlayer(self))
        else:
            pass
        
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
            for player in self.players:
                if player.alive:
                    player.update()
            
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
    speeddenom = 6
    def __init__(self, game):
        self.game = game
        #self.active = True
        self.rect = pygame.Rect(640, 145, 15, 15)
        
    def update(self):
        movequant = self.game.deltatime / self.speeddenom
        
        self.rect.move_ip(-movequant, 0)
        pygame.draw.rect(self.game.screen, red, self.rect)
        
        
        
class Player:
    defaultheight = 150
    r = 8 # radius
    scoredenom = 100
    
    def __init__(self, game, jumpspeeddenom, jumpheight):
        self.height = 0
        self.alive = True
        self.game = game
        #self.height = self.defaultheight
        self.direction = 0
        self.rect = pygame.Rect(20, self.defaultheight - int(self.r / 2), self.r, self.r)
        self.jumpspeeddenom = jumpspeeddenom
        self.jumpheight = jumpheight
        self.score = 0
        self.rawscore = 0
        
    def update(self):
        self.rawscore += int(self.game.deltatime / Block.speeddenom)
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
                self.alive = False
                print("PLAYER DIED")
        scoretext = self.game.font.render(str(self.score), True, green)
        self.game.screen.blit(scoretext, (10, 10))
        
class ManualPlayer(Player):
    jumpspeeddenom = 5
    jumpheight = 60
    def __init__(self, game):
        super().__init__(game, self.jumpspeeddenom, self.jumpheight)
    
    def update(self):
        for e in self.game.events:
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE) and (self.direction == 0):
                self.direction = 1
        super().update()
    
game = Game()
    
