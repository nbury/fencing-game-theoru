from model import boutModel
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np
import seaborn as sn
import sys
import random
from alive_progress import alive_bar

'''
Data notes:
Most data is from the Women's world championship in 2018, some bouts are from other tournaments, but using the same fencers around the same time
Data recorded:
names of each fencer
for each point:
    who won the point
    how they won it (offensive,defensive, counterattack)
    what each fencer did (quick, defensive, long)

Things I wish i had recorded:
    did the initial action decide the point, ie. was there a significant right of way switch
    some way to differentiate between the call: "attack is no, attack"
        a defensive manuever resulting in a right of way switch, so an offensive point from a defensive action
        however, it is not clear whether or not this should be offensive since often times the 
        second attack could be considered more of a riposte than its own attack
    lefthanded vs righthanded (this is extremely important)
Things I wanted to do if I had the time:
    record every action from each point in a more detailed way, rather than just offense/defense/counter

'''
def covariance(x, y):
    # Finding the mean of the series x and y
    mean_x = sum(x)/float(len(x))
    mean_y = sum(y)/float(len(y))
    # Subtracting mean from the individual elements
    sub_x = [i - mean_x for i in x]
    sub_y = [i - mean_y for i in y]
    numerator = sum([sub_x[i]*sub_y[i] for i in range(len(sub_x))])
    denominator = len(x)-1
    cov = numerator/denominator
    return cov

def isValid(point):
    if point['score'] != 'l' and point['score'] != 'r':
        return False
    if point['type'] != 'd' and point['type'] != 'o' and point['type'] != 'c':
        return False
    if point['leftAction'] != 'q' and point['leftAction'] != 'd' and point['leftAction'] != 'l':
        return False
    if point['rightAction'] != 'q' and point['rightAction'] != 'd' and point['rightAction'] != 'l':
        return False
    return True

def calculateAccuracy(fencers,data,scalars, skip_marked = False, only_marked = False):
    num_correct = 0
    num_total = 0
    for bout in data['bouts']:
        if skip_marked and 'marked' in bout:
            continue
        if only_marked and not 'marked' in bout:
            continue
        model = boutModel(fencers[bout['leftName']]['data_array'],fencers[bout['rightName']]['data_array'],scalars,useRandom = useRandom)
        for point in bout['points']:
            if not isValid(point):
                continue
            num_total+=1
            leftAction = point['leftAction']
            rightAction = point['rightAction']

            predictedWinner = model.predictWinner(leftAction,rightAction)
            actualWinner = point['score']
            if predictedWinner == actualWinner:
                num_correct+=1
    return num_correct/num_total

useRandom = False
skip_calcs = True
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg == '-r':
            useRandom = True
        if arg == '-s':
            skip_calcs = False


data = {}
with open('data.json','r') as f:
    data = json.load(f)
fencers = {}
print("Total number of bouts: ", len(data['bouts']))
print("Total number of points: ", sum(len(bout['points']) for bout in data['bouts']))
marked_bouts = random.sample(data['bouts'],3)
for bout in marked_bouts:
    bout['marked'] = True
for bout in data['bouts']:
    leftFencer = bout['leftName']
    rightFencer = bout['rightName']
    if leftFencer not in fencers:
        fencers[leftFencer] = {
            'offensive points': 0,
            'defensive points': 0,
            'total points won': 0,
            'speed points': 0,
            'total points': 0,
            'total points predicted correctly': 0,
            'num bouts': 0,
        }
    if rightFencer not in fencers:
        fencers[rightFencer] = {
            'offensive points': 0,
            'defensive points': 0,
            'total points won': 0,
            'speed points': 0,
            'total points': 0,
            'total points predicted correctly': 0,
            'num bouts': 0,
        }
    fencers[leftFencer]['num bouts']+=1
    fencers[rightFencer]['num bouts']+=1
    for point in bout['points']:
        if not isValid(point):
            continue
        fencers[leftFencer]['total points'] += 1
        fencers[rightFencer]['total points'] += 1
        if point['score'] == 'l':
            fencers[leftFencer]['total points won'] += 1
            if point['type'] == 'o':
                fencers[leftFencer]['offensive points'] += 1
                if point['leftAction'] == 'd':
                    fencers[leftFencer]['defensive points'] += 1
            elif point['type'] == 'd':
                fencers[leftFencer]['defensive points'] += 1
            elif point['type'] == 'c':
                fencers[leftFencer]['speed points'] += 1
                fencers[leftFencer]['defensive points'] += 1
            
            if point['leftAction'] == point['rightAction']:
                fencers[leftFencer]['speed points'] += 1
        else:
            fencers[rightFencer]['total points won'] += 1
            if point['type'] == 'o':
                fencers[rightFencer]['offensive points'] += 1
                if point['rightAction'] == 'd':
                    fencers[rightFencer]['defensive points'] += 1
            elif point['type'] == 'd':
                fencers[rightFencer]['defensive points'] += 1

            elif point['type'] == 'c':
                fencers[rightFencer]['speed points'] += 1
                fencers[rightFencer]['defensive points'] += 1
            
            if point['leftAction'] == point['rightAction']:
                fencers[rightFencer]['speed points'] += 1

for fencer in fencers:
    fencers[fencer]['data_array'] = [
        fencers[fencer]['offensive points'] / fencers[fencer]['total points won'],
        fencers[fencer]['defensive points'] / fencers[fencer]['total points won'],
        .5+fencers[fencer]['speed points'] / fencers[fencer]['total points won'],
        fencers[fencer]['total points won'] / fencers[fencer]['total points']
    ]
    print(fencer, ": ", fencers[fencer]['data_array'], ' (',fencers[fencer]['num bouts'],')')

num_correct = 0
num_total = 0
type_correct = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dd': 0,
    'dl': 0,
    'll': 0
}
type_count = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dd': 0,
    'dl': 0,
    'll': 0  
}
best_acc = 0
best_scalars = [0.2, 0.1, 0.1, 0.9, 3.9]

if not skip_calcs:
    with alive_bar((19**4)) as bar:
#        for s0 in np.arange(.1,2,.1):
#            for s1 in np.arange(.1,2,.1):
#               for s2 in np.arange(.1,2,.1):
#                    for s3 in np.arange(.1,2,.1):
                        for s4 in np.arange(.1,20,.1):
                            scalars = [0.2, 0.1, 0.1, 0.9,s4]
                            acc = calculateAccuracy(fencers,data,scalars,skip_marked=True)
                            if useRandom:
                                acc = 0
                                for i in range(100):
                                    acc +=.01* calculateAccuracy(fencers,data,scalars,skip_marked=True)

                            bar()
                            if acc > best_acc:
                                best_acc = acc
                                best_scalars = scalars
print("Test Set Accuracy: ", calculateAccuracy(fencers,data,best_scalars,only_marked=True))

#print("Best accuracy: ", best_acc)
row_splits = []
generalized_splits = []
for bout in data['bouts']:
    model = boutModel(fencers[bout['leftName']]['data_array'],fencers[bout['rightName']]['data_array'],best_scalars, useRandom = useRandom)
    for point in bout['points']:
        if not isValid(point):
            continue
        
        leftAction = point['leftAction']
        rightAction = point['rightAction']
        pair_type = leftAction + rightAction
        if pair_type == 'dq':
            pair_type = 'qd'
        elif pair_type == 'lq':
            pair_type = 'ql'
        elif pair_type == 'ld':
            pair_type = 'dl'

        type_count[pair_type] += 1

        predictedWinner = model.predictWinner(leftAction,rightAction)
        
        if fencers[bout['leftName']]['num bouts'] > 2 and fencers[bout['rightName']]['num bouts'] > 2:
            num_total+=1
        actualWinner = point['score']
        if predictedWinner == actualWinner:
            if fencers[bout['leftName']]['num bouts'] > 2 and fencers[bout['rightName']]['num bouts'] > 2: 
                num_correct+=1
            type_correct[pair_type] += 1
            
            if point['score'] == 'l':
                fencers[bout['leftName']]['total points predicted correctly'] += 1
            elif point['score'] == 'r':
                fencers[bout['rightName']]['total points predicted correctly'] += 1
        #print("[",leftAction,',',rightAction,'] :',predictedWinner,'/',actualWinner)
        model_gen_splits, model_row_splits = model.get_splits()
        generalized_splits.extend(model_gen_splits)
        row_splits.extend(model_row_splits)
plt.clf()
generalized_splits = [x for x in generalized_splits if x > 0]
row_splits = [x for x in row_splits if x > 0]
plt.hist(generalized_splits, bins = 100)
plt.savefig("graphs/Generalized Splits.png")
plt.clf()

plt.hist(row_splits, bins = 100)
plt.savefig("graphs/RoW Splits.png")
print("**************** Best Accuracy ****************")
print(best_scalars)
print(num_correct/num_total)
print("**************** Type Accuracy ****************")
for pair_type in type_count:
    print(pair_type, ": ", type_correct[pair_type]/type_count[pair_type], "  (", type_count[pair_type],")")
print("**************** Accuracy by Fencer **************** ")
plt.clf()
Y = [fencers[fencer]['total points predicted correctly']/fencers[fencer]['total points won'] for fencer in fencers]
X = [fencers[fencer]['total points'] for fencer in fencers]
plt.scatter(X,Y)
plt.plot(np.unique(X), np.poly1d(np.polyfit(X, Y, 5))(np.unique(X)))
plt.savefig('graphs/Accuracy by Fencer.png')
plt.clf()


X = [covariance([fencers[fencer]['data_array'][i]  for fencer in fencers],Y) for i in range(4)]
labels = ['Offensive', 'Defensive', 'Speed', 'Overall']
fig = plt.figure()
plt.bar(labels,X)
plt.savefig('graphs/Characteristic Covariance.png')

plt.clf()
Y = [type_correct[pair_type]/type_count[pair_type] if pair_type !='dd' else 0 for pair_type in type_count]
X = [type_count[pair_type] if pair_type !='dd' else 0 for pair_type in type_count]
X.remove(0)
Y.remove(0)
plt.scatter(X,Y)
plt.plot(np.unique(X), np.poly1d(np.polyfit(X, Y, 1))(np.unique(X)))
plt.savefig('graphs/Type Accuracy by Number of Type.png')

for fencer in fencers:
    print(fencer, ": ", fencers[fencer]['total points predicted correctly']/fencers[fencer]['total points won'], "  (", fencers[fencer]['total points won'],")")
# Analyze decisions after winning a point
num_same_action = 0
num_different_action = 0
num_same_action_won = 0
num_different_action_won = 0
for bout in data['bouts']:
    last_win = ''
    last_win_action = ''
    for point in bout['points']:
        if last_win == 'l':
            if point['leftAction'] == last_win_action:
                num_same_action+=1
                if point['score'] == 'l':
                    num_same_action_won+=1
            else:
                num_different_action+=1
                if point['score'] == 'l':
                    num_different_action_won+=1
        elif last_win == 'r':
            if point['rightAction'] == last_win_action:
                num_same_action+=1
                if point['score'] == 'r':
                    num_same_action_won+=1
            else:
                num_different_action+=1
                if point['score'] == 'r':
                    num_different_action_won+=1
        last_win = point['score']
        last_win_action = point['leftAction'] if point['score'] == 'l' else point['rightAction']

print("*************** Action analysis after winning point *****************")       
print("Same action: ", num_same_action)
print("Different action: ", num_different_action)
print("Same action won: ", num_same_action_won)
print("Different action won: ", num_different_action_won)
print("Same action win percent: ", num_same_action_won/num_same_action)
print("Different action win percent: ", num_different_action_won/num_different_action)

action_pair_loss_loss = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dq': 0,
    'dd': 0,
    'dl': 0,
    'lq': 0,
    'ld': 0,
    'll': 0
}
action_pair_loss_win = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dq': 0,
    'dd': 0,
    'dl': 0,
    'lq': 0,
    'ld': 0,
    'll': 0
}
action_pair_win_loss = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dq': 0,
    'dd': 0,
    'dl': 0,
    'lq': 0,
    'ld': 0,
    'll': 0
}
action_pair_win_win = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dq': 0,
    'dd': 0,
    'dl': 0,
    'lq': 0,
    'ld': 0,
    'll': 0
}
action_pairs = {
    'qq': 0,
    'qd': 0,
    'ql': 0,
    'dq': 0,
    'dd': 0,
    'dl': 0,
    'lq': 0,
    'ld': 0,
    'll': 0
}
for bout in data['bouts']:
    last_action_left = ''
    last_action_right = ''
    last_win = ''
    last_winning_action = ''
    for point in bout['points']:
        if not isValid(point):
            last_action_left = ''
            last_action_right = ''
            last_win = ''  
            last_winning_action = ''
            continue          
        if last_action_left == '':
            last_action_left = point['leftAction']
            last_action_right = point['rightAction']
            continue
        if last_action_left+point['leftAction'] in action_pairs:
            action_pairs[last_action_left+point['leftAction']]+=1
        if last_action_right+point['rightAction'] in action_pairs:
            action_pairs[last_action_right+point['rightAction']]+=1

        if point['score'] == 'l':
            if last_win == 'r':
                action_pair_loss_win[last_action_left+point['leftAction']]+=1
                action_pair_win_loss[last_action_right+point['rightAction']]+=1
            elif last_win == 'l':
                action_pair_win_win[last_action_left+point['leftAction']]+=1
                action_pair_loss_loss[last_action_right+point['rightAction']]+=1

        elif point['score'] == 'r':
            if last_win == 'r':
                action_pair_win_win[last_action_right+point['rightAction']]+=1
                action_pair_loss_loss[last_action_left+point['leftAction']]+=1
                
            elif last_win == 'l':
                action_pair_loss_win[last_action_right+point['rightAction']]+=1
                action_pair_win_loss[last_action_left+point['leftAction']]+=1
        winning_action = point['leftAction'] if point['score'] == 'l' else point['rightAction']
        last_winning_action = winning_action
        last_action_left = point['leftAction']
        last_action_right = point['rightAction']
        last_win = point['score']

print("**************** Action pair Counts ****************")
for action_pair in action_pairs:
    print(action_pair, ": ", action_pairs[action_pair])

# P(win_current | last_action, current_action )
print("**************** Action pair 2nd win analysis ****************")
for a in ['q', 'd', 'l']:
    print("------ ", a, " ------")
    for p in ['q', 'd', 'l']:
                print(a+p, ": ", (action_pair_loss_win[a+p]+action_pair_win_win[a+p])/(action_pair_win_win[a+p]+action_pair_win_loss[a+p]+action_pair_loss_loss[a+p]+action_pair_loss_win[a+p]))
    #print(ap, ": ", (action_pair_loss_win[ap] + action_pair_win_win[ap] ) / action_pairs[ap])
aps = ['qq', 'qd', 'ql', 'dq', 'dd', 'dl', 'lq', 'ld', 'll']
X = [action_pairs[ap] for ap in aps]
Y = [(action_pair_loss_win[ap]+action_pair_win_win[ap])/(action_pair_win_win[ap]+action_pair_win_loss[ap]+action_pair_loss_loss[ap]+action_pair_loss_win[ap]) for ap in aps]
plt.clf()
plt.scatter(X,Y)
plt.plot(np.unique(X), np.poly1d(np.polyfit(X, Y, 1))(np.unique(X)))
plt.savefig('graphs/Action Pair Success Rate by Frequency.png')
# P(win_current | last_action, current_action && last_action => win )
print("**************** Action pair win - win analysis ****************")
for a in ['q', 'd', 'l']:
    print("------ ", a, " ------")
    for p in ['q', 'd', 'l']:
        print(a+p, ": ", action_pair_win_win[a+p]/(action_pair_win_win[a+p]+action_pair_win_loss[a+p]))

# P(win_current | last_action, current_action && last_action => loss )
print("**************** Action pair loss - win analysis ****************")
for a in ['q', 'd', 'l']:
    print("------ ", a, " ------")
    for p in ['q', 'd', 'l']:
                print(a+p, ": ", action_pair_loss_win[a+p]/(action_pair_loss_loss[a+p]+action_pair_loss_win[a+p]))



