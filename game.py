import pygame

black = (0,0,0)

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
        
        self.blocks = []
        self.players = []
        self.players.append(ManualPlayer(self))
        
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
            for player in self.players:
                if player.alive:
                    player.update()
            for block in self.blocks:
                if block.active:
                    block.update()
            
            pygame.display.flip()
            
        print("game aborted")
        pygame.quit()
        
class Player:
    defaultheight = 150
    r = 8 # radius
    def __init__(self, game, jumpdenom, jumpheight):
        self.height = 0
        self.alive = True
        self.game = game
        #self.height = self.defaultheight
        self.direction = 0
        self.rect = pygame.Rect(20, self.defaultheight - int(self.r / 2), self.r, self.r)
        self.jumpquant = 0
        self.jumpdenom = jumpdenom
        self.jumpheight = jumpheight
        
    def update(self):
        self.jumpquant = self.game.deltatime / self.jumpdenom
        self.rect.move_ip(0, self.jumpquant * self.direction * -1)
        if self.rect.centery <= self.defaultheight - self.jumpheight:
            self.direction = -1
        if self.rect.centery >= self.defaultheight:
            self.direction = 0
            self.rect.centery = self.defaultheight
        pygame.draw.circle(self.game.screen, black, self.rect.center, self.r)
        
class ManualPlayer(Player):
    def __init__(self, game):
        super().__init__(game, 5, 60)
    
    def update(self):
        for e in self.game.events:
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE) and (self.direction == 0):
                self.direction = 1
        super().update()
    
game = Game()
    
