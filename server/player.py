class Player:
    def __init__(self, pid, name, x, y):
      self.pid = pid
      self.name = name
      self.x = x
      self.y = y
    
    def check_collision(self,player):
        if self.x == player.x :
            if self.y == player.y:
                return True
        return False



 
    
