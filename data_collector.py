import json

    
def recordBout():
    bout_data = {'points':[]}
    leftName = input("Enter the name of the left player: ")
    rightName = input("Enter the name of the right player: ")
    bout_data["leftName"] = leftName
    bout_data["rightName"] = rightName
    
    while 1:   
        point  = {}
        point['score'] = input("enter who won the point (l/r): ")    
        point['type'] = input("enter the type of point (d/o/c): ")
        point['leftAction'] = input("enter the left action (q/d/l): ")
        point['rightAction'] = input("enter the right action (q/d/l): ")
        bout_data['points'].append(point)
        cont = input("continue? (y/n): ")
        if cont == 'n':
            break
    return bout_data


with open("data.json", "w") as f:
    data = {'bouts':[]}
    while 1:
        bout = recordBout()
        data['bouts'].append(bout)
        cont = input("new bout? (y/n): ")
        json.dump(data, f,indent = 2)
        if cont == 'n':
            break  
        
