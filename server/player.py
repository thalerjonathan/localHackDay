class Player:

    def __init__(self, pid, name, x, y, seeker):
        self.pid = pid
        self.name = name
        self.x = x
        self.y = y
        self.seeker = seeker
    
    def check_collision(self,player):
        return self.calculate_man_distance(player)==0

    def calculate_man_distance(self, player):
        return abs(self.x-player.x) + abs(self.y-player.y)
    