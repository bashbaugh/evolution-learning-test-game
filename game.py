import pygame

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
        self.players.append(manualPlayer(self))
        
        self.rungame()
        
    def rungame(self):
        print("running game")
        while not self.done:
            self.events = pygame.event.get()
            for e in self.events:
                if (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE) or (e.type == pygame.QUIT):
                    self.done = True
            self.screen.fill((255, 255, 255))
            self.deltatime = self.clock.tick()
            for player in self.players:
                if player.alive:
                    player.update
            for block in self.blocks:
                if block.active:
                    block.update()
            
            pygame.display.flip()
            
        print("game aborted")
        pygame.quit()
        
class manualPlayer():
    def __init__(self, game):
        self.height = 0
        self.alive = True
        self.game = game
        
    def update(self):
        for e in self.game.events:
            if e.type = pygame.keydown and e.key == pygame.K_SPACE:
                
                    
    
game = Game()
    
