import random
import math

class boutModel():
    
    def __init__(self, left,right, scalars):
        # O,D,S,A    
        self.left = left
        self.right = right
        self.scalars = scalars

        
    def predictWinner(self, leftAction, rightAction):
        if leftAction == 'q':
            if rightAction == 'q':
                return self.rightOfWay()
            elif rightAction == 'd':
                return self.generalized('l')
            elif rightAction == 'l':
                return self.rightOfWay()
        
        elif leftAction == 'd':
            if rightAction == 'q':
                return self.generalized('r')
            elif rightAction == 'd':
                return self.generalized(self.rightOfWay())
            elif rightAction == 'l':
                return self.generalized('r')

        elif leftAction == 'l':
            if rightAction == 'q':
                return self.rightOfWay()
            elif rightAction == 'd':
                return self.generalized('l')
            elif rightAction == 'l':
                return self.generalized(self.rightOfWay())
        
    def rightOfWay(self):
        pL = self.left[2] * self.scalars[2]
        pR = self.right[2] * self.scalars[2]
        split = math.log(self.scalars[4]*(pL/(pL+pR))+1)
        if split > random.random():
            return 'l'
        return 'r'
    def generalized(self,rightOfWay):
        
        if rightOfWay == 'l':
            pL = ( (self.left[0]*self.scalars[0]  + self.left[2]*self.scalars[2]) /2 ) + self.left[3]*self.scalars[3]
            pR = self.right[1]*self.scalars[1] + self.right[3]*self.scalars[3]
            split = math.log(self.scalars[4]*(pL/(pL+pR))+1)
            if split > random.random():
                return 'l'
            return 'r'
        else:
            pL = ( (self.left[1]*self.scalars[1]  + self.left[2]*self.scalars[2]) /2 )+ self.left[3]*self.scalars[3]
            pR = self.right[0]*self.scalars[0] + self.right[3]*self.scalars[3]
            split = math.log(self.scalars[4]*(pL/(pL+pR))+1)
            if split > random.random():
                return 'l'
            return 'r'