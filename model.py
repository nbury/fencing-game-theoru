import random
import math
import matplotlib.pyplot as plt

class boutModel():
    
    def __init__(self, left,right, scalars,useRandom = False):
        # O,D,S,A    
        self.left = left
        self.right = right
        self.scalars = scalars
        self.useRandom = useRandom
        self.generalized_splits = []
        self.row_splits = []

        
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
        split = .5-pL/(pL+pR)
        
        if split < 0:
            split = -1*math.log(-1*self.scalars[4]*split+1)+.5
        else:
            split = math.log(self.scalars[4]*split+1)+.5
        self.row_splits.append(split)
        threshold = random.random() if self.useRandom else .5
        if split > threshold:
            return 'l'
        return 'r'
    def generalized(self,rightOfWay):
        
        if rightOfWay == 'l':
            pL = ( (self.left[0]*self.scalars[0]  + self.left[2]*self.scalars[2]) /2 ) + self.left[3]*self.scalars[3]
            pR = self.right[1]*self.scalars[1] * self.right[3]*self.scalars[3]
            split = .5-pL/(pL+pR)
            if split < 0:
                split = -1*math.log(-1*self.scalars[4]*split+1)+.5
            else:
                split = math.log(self.scalars[4]*split+1)+.5
            self.generalized_splits.append(split)
            threshold = random.random() if self.useRandom else .5
            if split > threshold:
                return 'l'
            return 'r'
        else:
            pL = ( (self.right[1]*self.scalars[1]  + self.right[2]*self.scalars[2]) /2 )+ self.right[3]*self.scalars[3]
            pR = self.left[0]*self.scalars[0] + self.left[3]*self.scalars[3]
            split = .5-pL/(pL+pR)
            if split < 0:
                split = -1*math.log(-1*self.scalars[4]*split+1)+.5
            else:
                split = math.log(self.scalars[4]*split+1)+.5
            self.generalized_splits.append(split)
            threshold = random.random() if self.useRandom else .5
            if split > threshold:
                return 'l'
            return 'r'
    def get_splits(self):
        return self.generalized_splits, self.row_splits
