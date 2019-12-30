#author: David Munoz Constantine
from dinner import *
import random
import sys
import numpy as np
from datetime import datetime
from itertools import permutations

#here is where the astar g+h is calculated
def getBestForLocation(party, location, noise):
  aliensNotSeated = party.aliensNotSeated.copy()
  scoresPerAlien = {}
  originalScore = party.getBarScore()
  #for each alien that is not seated find its astar score
  for alienNotSeated in aliensNotSeated:
    party.seatAlienAt(alienNotSeated, location)
    #g score is the score of the table before they were seated + the score of 
    #the table once they seat
    g = party.getLocationScore(location) + originalScore
    h = -9999999999
    adjacentLocations = party.getEmptyAdjacentLocations(location)
    #get all pairs that can seat in the adjacent empty location to the current alien
    #will calculate maximum score possible by seating aliens adjacent and across
    remainingPairs = permutations(party.aliensNotSeated, len(adjacentLocations)) 
    for pair in remainingPairs:
      tempScore = 0
      #seat each alien and calculate its immediate impact on the table
      for i in range(len(adjacentLocations)):
        party.seatAlienAt(pair[i], adjacentLocations[i])
        tempScore += party.getLocationScore(adjacentLocations[i])
      tempScore += g
      if tempScore > h:
        h = tempScore
      #undo the seating for trying next pair
      for i in range(len(adjacentLocations)):
        party.unseatLocation(adjacentLocations[i])
    scoresPerAlien[alienNotSeated] = g + h
    #undo and try next alien
    party.unseatLocation(location)  
  #return sorted aliens by score, want to sometimes explore a random path
  return swap_random(sorted(scoresPerAlien.items(), key=lambda x: x[1], reverse=True), noise)

#only want to exploare at most maxNodex, since it can become exponential
#modified code from https://stackoverflow.com/questions/47724017/swap-two-values-randomly-in-list
def swap_random(seq, noise=0.25, maxNodes=12):
  if len(seq) <=3:
    return seq
  if random.random() > noise:
    return seq[:maxNodes]
  idx = range(len(seq))
  i1, i2 = random.sample(idx, 2)
  seq[i1], seq[i2] = seq[i2], seq[i1]
  return seq[:maxNodes]
  
def seatNextAlien(party, locations, timeStart, maxSeconds, solution, noise):
  if len(locations) == 0:
    return solution
  if (datetime.now() - timeStart).total_seconds() < maxSeconds:
    for loc in locations:
      #get sorted list of aliens that would give the best score at loc
      scoresPerAlien = getBestForLocation(party=party, location=loc, noise=noise)
      for pair in scoresPerAlien:
        #for each of those poeple, seat them and find the next best alien for
        #empty locations
        party.seatAlienAt(pair[0], loc)
        adjLocations = party.getEmptyAdjacentLocations(loc)
        if (datetime.now() - timeStart).total_seconds() < maxSeconds:
          solution = seatNextAlien(party,
                                    adjLocations,
                                    timeStart, 
                                    maxSeconds, 
                                    solution, 
                                    noise)
        #once the table is full, get the scores and if it is better, record it
        if party.isBarFull():
          currentScore = party.getBarScore()
          if currentScore > solution['max_score']:
            solution = party.seatingDict()
            solution['max_score'] = currentScore
        #unseat the last alien seated and continue looking
        party.unseatLocation(loc)
        if (datetime.now() - timeStart).total_seconds() > maxSeconds:
          break
  return solution

def solveAStar(n, preferenceMatrix, timeStart, maxSeconds=60, noise=0.2):
  #sum rows and columns for each alien. alien with lowest scores
  #must be seated at corner since it is not liked and does not like others
  r = np.sum(preferenceMatrix, axis=1)
  c = np.sum(preferenceMatrix, axis=0)
  scores = []
  for i in range(len(r)):
    scores.append(r[i] + c[i])
  worstAliens = np.argsort(scores) + 1
  party = Dinner(n, preferenceMatrix)
  solution = {"max_score":-500}
  for badAlien in worstAliens:
    party.seatAlienAt(badAlien, 0)
    adjLocations = party.getEmptyAdjacentLocations(0)
    solution = seatNextAlien(party=party,
                               locations=adjLocations,
                               timeStart=timeStart,
                               maxSeconds=maxSeconds,
                               solution=solution,
                               noise=noise)
    party.unseatLocation(0)
    if (datetime.now() - timeStart).total_seconds() >= maxSeconds:
      break
  maxScore = solution.pop("max_score")
  return maxScore, sorted(solution.items(), key=lambda x: x[1], reverse=False)

def main(maxSeconds=60):
  file = open(sys.argv[1], "r")
  lines = file.readlines()
  n = int(lines[0].rstrip())
  preferenceMatrix = []
  for line in lines[1:]:
    preferenceMatrix.append([int(x) for x in line.rstrip().split(" ")])
  score, couch = solveAStar(n, preferenceMatrix, timeStart=datetime.now(), 
                              maxSeconds=maxSeconds, noise=0.2)
  print(score)
  for location, alien in couch:
    print(alien, location)
  
if __name__ == '__main__':
  if len(sys.argv) > 2:
    main(int(sys.argv[2]))
  else:
    print("Need preference file as argument and max running time")