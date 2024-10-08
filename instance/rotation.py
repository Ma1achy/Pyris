from utils import Vec2

class RotationSystem():
    def __init__(self, type):
        """
        Rotation system for the game, kick tables for each piece type and rotation type
        
        args:
            type (str): The type of rotation system to use
        """
        self.type = type
        
        if self.type == 'SRS': # Super Rotation System (Guideline)
            self.TSZLJ_KICKS = {
                '0->1': [Vec2(0, 0), Vec2(-1, 0), Vec2(-1, +1), Vec2(0, -2), Vec2(-1, -2)],
                '1->0': [Vec2(0, 0), Vec2(+1, 0), Vec2(+1, -1), Vec2(0, +2), Vec2(+1, +2)],
                
                '1->2': [Vec2(0, 0), Vec2(+1, 0), Vec2(+1, -1), Vec2(0, +2), Vec2(+1, +2)],
                '2->1': [Vec2(0, 0), Vec2(-1, 0), Vec2(-1, +1), Vec2(0, -2), Vec2(-1, -2)],
                
                '2->3': [Vec2(0, 0), Vec2(+1, 0), Vec2(+1, +1), Vec2(0, -2), Vec2(+1, -2)],
                '3->2': [Vec2(0, 0), Vec2(-1, 0), Vec2(-1, -1), Vec2(0, +2), Vec2(-1, +2)],
                
                '3->0': [Vec2(0, 0), Vec2(-1, 0), Vec2(-1, -1), Vec2(0, +2), Vec2(-1, +2)],
                '0->3': [Vec2(0, 0), Vec2(+1, 0), Vec2(+1, +1), Vec2(0, -2), Vec2(+1, -2)],
            }
                
            self.I_KICKS = {     
                '0->1': [Vec2(0, 0), Vec2(-2, 0), Vec2(+1, 0), Vec2(-2, -1), Vec2(+1, +2)],
                '1->0': [Vec2(0, 0), Vec2(+2, 0), Vec2(-1, 0), Vec2(+2, +1), Vec2(-1, -2)],
                
                '1->2': [Vec2(0, 0), Vec2(-1, 0), Vec2(+2, 0), Vec2(-1, +2), Vec2(+2, -1)],
                '2->1': [Vec2(0, 0), Vec2(+1, 0), Vec2(-2, 0), Vec2(+1, -2), Vec2(-2, +1)],
                
                '2->3': [Vec2(0, 0), Vec2(+2, 0), Vec2(-1, 0), Vec2(+2, +1), Vec2(-1, -2)],
                '3->2': [Vec2(0, 0), Vec2(-2, 0), Vec2(+1, 0), Vec2(-2, -1), Vec2(+1, +2)],
                
                '3->0': [Vec2(0, 0), Vec2(+1, 0), Vec2(-2, 0), Vec2(+1, -2), Vec2(-2, +1)],
                '0->3': [Vec2(0, 0), Vec2(-1, 0), Vec2(+2, 0), Vec2(-1, +2), Vec2(+2, -1)],
            }
            
            self.O_KICKS = {
                '0->1': [Vec2(0, 0)],
                '1->0': [Vec2(0, 0)],
        
                '1->2': [Vec2(0, 0)],
                '2->1': [Vec2(0, 0)],
        
                '2->3': [Vec2(0, 0)],
                '3->2': [Vec2(0, 0)],
        
                '3->0': [Vec2(0, 0)],
                '0->3': [Vec2(0, 0)],
            }
            
            self.TSZLJ_180_KICKS = {
                '0->2': [Vec2(0, 0), Vec2(+1, 0), Vec2(+2, 0), Vec2(+1, +1), Vec2(+2, +1), Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, +1), Vec2(-2, +1), Vec2(0, -1), Vec2(+3, 0), Vec2(-3, 0)],
                '2->0': [Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, -1), Vec2(-2, -1), Vec2(+1, 0), Vec2(+2, 0), Vec2(+1, -1), Vec2(+2, -1), Vec2(0, +1), Vec2(-3, 0), Vec2(+3, 0)], 
                
                '1->3': [Vec2(0, 0), Vec2(0, +1), Vec2(0, +2), Vec2(-1, +1), Vec2(-1, +2), Vec2(0, -1), Vec2(0, -2), Vec2(-1, -1), Vec2(-1, -2), Vec2(+1, 0), Vec2(0, +3), Vec2(0, -3)],
                '3->1': [Vec2(0, 0), Vec2(0, +1), Vec2(0, +2), Vec2(+1, +1), Vec2(+1, +2), Vec2(0, -1), Vec2(0, -2), Vec2(+1, -1), Vec2(+1, -2), Vec2(-1, 0), Vec2(0, +3), Vec2(0, -3)],
            }
            
            self.I_180_KICKS = {
                '0->2': [Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(+1, 0), Vec2(+2, 0), Vec2(0, +1)],
                '2->0': [Vec2(0, 0), Vec2(+1, 0), Vec2(+2, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(0, -1)],
                
                '1->3': [Vec2(0, 0), Vec2(0, +1), Vec2(0, +2), Vec2(0, -1), Vec2(0, -2), Vec2(-1, 0)],
                '3->1': [Vec2(0, 0), Vec2(0, +1), Vec2(0, +2), Vec2(0, -1), Vec2(0, -2), Vec2(+1, 0)],
            }
            
            self.O_180_KICKS = {
                '0->2': [Vec2(0, 0)],
                '2->0': [Vec2(0, 0)],
            
                '1->3': [Vec2(0, 0)],
                '3->1': [Vec2(0, 0)],
            }

            # Kick table given to game instance
            self.kick_table = {
                '90': {'TSZLJ_KICKS': self.TSZLJ_KICKS, 'I_KICKS': self.I_KICKS, 'O_KICKS': self.O_KICKS},
                '180': {'TSZLJ_KICKS': self.TSZLJ_180_KICKS, 'I_KICKS': self.I_180_KICKS, 'O_KICKS': self.O_180_KICKS}
            }
            
    