#author: David Munoz Constantine
import enum

class Alien(enum.Enum):
  host = 1
  guest = 2

class Bar:
  def __init__(self, numberOfGuests, initialSeating=None):
    if initialSeating:
      self.seats = initialSeating
    else:
      self.seats = [0] * numberOfGuests
    self.seatedCount = 0
  
  def seatAlienAt(self, alien, location):
    self.seats[location] = alien
    self.seatedCount += 1
  
  def unseatLocation(self, location):
    alien = self.seats[location] 
    self.seats[location] = 0
    self.seatedCount -= 1
    return alien
    
  def alienAtLocation(self, location):
    return self.seats[location]
  
  def _seatsPerRow(self):
    return int(len(self.seats)/2)
  
  def getAdjacent(self, location):
    seatsPerRow = self._seatsPerRow()
    if location < seatsPerRow:
      if location == 0:
        return [1, seatsPerRow]
      if location == seatsPerRow-1:
        return [location - 1, seatsPerRow*2 -1]
      return [location - 1, location + 1, seatsPerRow + location]
    else:
      if location == seatsPerRow:
        return [location + 1, 0]
      if location == seatsPerRow*2 - 1:
        return [location - 1, seatsPerRow -1]
      return [location - 1, location + 1,  location - seatsPerRow]
    
  def getAlienLocation(self, alien):
    for i in range(len(self.seats)):
      if self.seats[i] == alien:
        return i
    return -1
  
  def _getSeating(self, start, multiplier):
    return self.seats[start:self._seatsPerRow() * multiplier]
  
  def getTopSeating(self):
    return self._getSeating(0, 1)
  
  def getBottomSeating(self):
    return self._getSeating(self._seatsPerRow(), 2)
  
  def isSeatingFull(self):
    return self.seatedCount == len(self.seats)
  
  def isLocationEmpty(self, location):
    return self.seats[location] == 0
  

class Dinner:
  
  def __init__(self, numberOfGuests, preferenceMatrix, initialSeating=None, safe=False):
    self.numberOfGuests = numberOfGuests
    assert len(preferenceMatrix) == numberOfGuests
    assert len(preferenceMatrix[0]) == numberOfGuests
    self.preferenceMatrix = preferenceMatrix
    if initialSeating:
      assert len(initialSeating) == numberOfGuests
      self.table = Bar(numberOfGuests, initialSeating)
    else:
      self.table = Bar(numberOfGuests)
    self.aliensSeated = []
    self.aliensNotSeated = [i+1 for i in range(numberOfGuests)]
    self.allRoles = {}
    for i in range(numberOfGuests):
      if i < numberOfGuests/2:
        self.allRoles[i+1] = Alien.host
      else:
        self.allRoles[i+1] = Alien.guest
    self.safe = safe
    
  def _isValidAlien(self, alien):
    if alien > self.numberOfGuests or alien < 0:
      return False
    return True
  
  def _isValidLocation(self, location):
    if location >= self.numberOfGuests or location < 0:
      return False
    return True
  
  def getAdjacentLocations(self, location):
    return self.table.getAdjacent(location)
  
  def getEmptyAdjacentLocations(self, location):
    adj = self.table.getAdjacent(location)
    return [loc for loc in adj if self.alienAtLocation(loc) == 0]
  
  def role(self, alien):
    if self.safe:
      assert self._isValidAlien(alien)
    return self.allRoles[alien]
  
  def preference(self, alien1, alien2):
    if self.safe:
      assert self._isValidAlien(alien1)
      assert self._isValidAlien(alien2)
    return self.preferenceMatrix[alien1-1][alien2-1]
  
  def seatAlienAt(self, alien, location):
    if self.safe:
      assert self._isValidAlien(alien)
      assert self._isValidLocation(location)
      assert self.table.isLocationEmpty(location)
    self.table.seatAlienAt(alien, location)
    self.aliensSeated.append(alien)
    self.aliensNotSeated.remove(alien)
    if self.safe:
      assert len(self.aliensNotSeated) + len(self.aliensSeated) == self.numberOfGuests
  
  def unseatAlien(self, alien):
    if self.safe:
      assert self._isValidAlien(alien)
    location = self.table.getAlienLocation(alien)
    if self.safe:
      assert location >= 0
    self.table.unseatLocation(location)
    self.aliensSeated.remove(alien)
    self.aliensNotSeated.append(alien)
    if self.safe:
      assert len(self.aliensNotSeated) + len(self.aliensSeated) == self.numberOfGuests
    return location
    
  def unseatLocation(self, location):
    if self.safe:
      assert self._isValidLocation(location)
      assert self.table.isLocationEmpty(location) == False
    alien = self.table.unseatLocation(location)
    self.aliensSeated.remove(alien)
    self.aliensNotSeated.append(alien)
    if self.safe:
      assert len(self.aliensNotSeated) + len(self.aliensSeated) == self.numberOfGuests
    return alien
    
  def swapAliens(self, alien1, alien2):
    location1 = self.unseatAlien(alien1)
    location2 = self.unseatAlien(alien2)
    self.seatAlienAt(alien1, location2)
    self.seatAlienAt(alien2, location1)
  
  def alienAtLocation(self, location):
    return self.table.alienAtLocation(location)
  
  def isBarFull(self):
    return self.table.isSeatingFull()
  
  #returns a dictionary get values location:alien
  def getCurrentSeating(self):
    return self.table.seats
  
  def seatingDict(self):
    res = {}
    for i in range(self.numberOfGuests):
      res[i] = self.alienAtLocation(i)
    return res
  
  def getLocationScore(self, location):
    if self.safe:
      assert self._isValidLocation(location)
    score = 0
    top = self.table.getTopSeating()
    bottom = self.table.getBottomSeating()
    seatsPerRow = self.table._seatsPerRow()
    if location < seatsPerRow:
      seating = top
      if bottom[location] > 0:
        if self.role(top[location]) != self.role(bottom[location]):
          score += 2
        score += self.preference(top[location], bottom[location])
        score += self.preference(bottom[location], top[location])
    else:
      seating = bottom
      location -=seatsPerRow
      if top[location] > 0:
        if self.role(top[location]) != self.role(bottom[location]):
          score += 2
        score += self.preference(top[location], bottom[location])
        score += self.preference(bottom[location], top[location])
    if location < seatsPerRow-1:
      if seating[location+1] > 0:
        if self.role(seating[location]) != self.role(seating[location+1]):
          score += 1
        score += self.preference(seating[location], seating[location+1])
        score += self.preference(seating[location+1], seating[location])
    if location > 0:
      if seating[location-1] > 0:
        if self.role(seating[location]) != self.role(seating[location-1]):
          score += 1
        score += self.preference(seating[location], seating[location-1])
        score += self.preference(seating[location-1], seating[location])
          
    return score 
      
  def getBarScore(self):
    score = 0
    top = self.table.getTopSeating()
    for i in range(len(top)-1):
      if top[i] > 0 and top[i+1] > 0:
        if self.role(top[i]) != self.role(top[i+1]):
          score += 1
        score += self.preference(top[i], top[i+1])
        score += self.preference(top[i+1], top[i])
    bottom = self.table.getBottomSeating()
    for i in range(len(bottom)-1):
      if bottom[i] > 0 and bottom[i+1] > 0:
        if self.role(bottom[i]) != self.role(bottom[i+1]):
          score += 1
        score += self.preference(bottom[i], bottom[i+1])
        score += self.preference(bottom[i+1], bottom[i])
    for i in range(len(top)):
      if top[i] > 0 and bottom[i] > 0:
        if self.role(top[i]) != self.role(bottom[i]):
          score += 2
        score += self.preference(top[i], bottom[i])
        score += self.preference(bottom[i], top[i])
    return score