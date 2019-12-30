#author: David Munoz Constantine
import pytest
from dinner import *

@pytest.fixture
def small_dinner():
  return Dinner(4, [[0, 12, 10, -50],[10, 0, -50, 10],[10, -50, 0, 10],[-50, 10, 10, 0]], safe=True)

@pytest.fixture
def small_dinner_two():
  return Dinner(4, [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]], safe=True)

def test_perfect_score(small_dinner):
  small_dinner.seatAlienAt(1, 0)
  small_dinner.seatAlienAt(2, 1)
  small_dinner.seatAlienAt(3, 2)
  small_dinner.seatAlienAt(4, 3)
  assert small_dinner.getTableScore() == 86
  
def test_location_score(small_dinner):
  small_dinner.seatAlienAt(1, 0)
  assert small_dinner.getLocationScore(0) == 0
  small_dinner.seatAlienAt(2, 1)
  assert small_dinner.getLocationScore(0) == 22
  small_dinner.seatAlienAt(3, 2)
  assert small_dinner.getLocationScore(0) == 44
  small_dinner.seatAlienAt(4, 3)
  assert small_dinner.getLocationScore(0) == 44
  
def test_score(small_dinner):
  small_dinner.seatAlienAt(1, 0)
  small_dinner.seatAlienAt(4, 1)
  small_dinner.seatAlienAt(3, 2)
  small_dinner.seatAlienAt(2, 3)
  assert small_dinner.getTableScore() == -154
  
def test_score_no_preference_one(small_dinner_two):
  small_dinner_two.seatAlienAt(1, 0)
  small_dinner_two.seatAlienAt(4, 1)
  small_dinner_two.seatAlienAt(3, 2)
  small_dinner_two.seatAlienAt(2, 3)
  assert small_dinner_two.getTableScore() == 6
  
def test_score_no_preference_two(small_dinner_two):
  small_dinner_two.seatAlienAt(1, 0)
  small_dinner_two.seatAlienAt(3, 1)
  small_dinner_two.seatAlienAt(2, 2)
  small_dinner_two.seatAlienAt(4, 3)
  assert small_dinner_two.getTableScore() == 2
  
def test_current_seating(small_dinner):
  seats = small_dinner.getCurrentSeating()
  for i in range(len(seats)):
    assert seats[i] == 0
  small_dinner.seatAlienAt(1, 0)
  small_dinner.seatAlienAt(4, 1)
  seats = small_dinner.getCurrentSeating()
  assert seats[1] == 4
  small_dinner.seatAlienAt(3, 2)
  small_dinner.seatAlienAt(2, 3)
  seats = small_dinner.getCurrentSeating()
  assert seats[0] == 1
  assert seats[1] == 4
  assert seats[2] == 3
  assert seats[3] == 2

def test_is_table_full(small_dinner):
  assert small_dinner.isTableFull() is False
  small_dinner.seatAlienAt(2, 3)
  assert small_dinner.isTableFull() is False
  small_dinner.seatAlienAt(1, 0)
  small_dinner.seatAlienAt(4, 1)
  small_dinner.seatAlienAt(3, 2)
  assert small_dinner.isTableFull()

def test_alien_at_location_and_seating(small_dinner):
  assert small_dinner.alienAtLocation(2) == 0
  small_dinner.seatAlienAt(3, 2)
  assert small_dinner.alienAtLocation(2) == 3
  assert small_dinner.alienAtLocation(0) == 0
  
def test_unseat_alien(small_dinner):
  assert small_dinner.alienAtLocation(2) == 0
  small_dinner.seatAlienAt(3, 2)
  assert small_dinner.alienAtLocation(2) == 3
  assert small_dinner.alienAtLocation(0) == 0
  small_dinner.unseatAlien(3)
  assert small_dinner.alienAtLocation(2) == 0
  assert small_dinner.alienAtLocation(0) == 0

def test_unseat_location(small_dinner):
  assert small_dinner.alienAtLocation(2) == 0
  small_dinner.seatAlienAt(3, 2)
  assert small_dinner.alienAtLocation(2) == 3
  assert small_dinner.alienAtLocation(0) == 0
  small_dinner.unseatLocation(2)
  assert small_dinner.alienAtLocation(2) == 0
  assert small_dinner.alienAtLocation(0) == 0
  
def test_swap_aliens(small_dinner):
  small_dinner.seatAlienAt(3, 2)
  small_dinner.seatAlienAt(4, 0)
  assert small_dinner.alienAtLocation(2) == 3
  assert small_dinner.alienAtLocation(0) == 4
  small_dinner.swapAliens(3, 4)
  assert small_dinner.alienAtLocation(2) == 4
  assert small_dinner.alienAtLocation(0) == 3
  small_dinner.swapAliens(3, 4)
  assert small_dinner.alienAtLocation(2) == 3
  assert small_dinner.alienAtLocation(0) == 4
  
def test_preference(small_dinner):
  assert small_dinner.preference(1,2) == 12
  assert small_dinner.preference(2,1) == 10
  
def test_role(small_dinner):
  assert small_dinner.role(1) == Alien.host
  assert small_dinner.role(3) == Alien.guest
  
def test_adjacent_locations(small_dinner):
  assert small_dinner.getAdjacentLocations(0) == [1, 2]
  assert small_dinner.getAdjacentLocations(1) == [0, 3]

def test_empty_adjacent_locations(small_dinner):
  assert small_dinner.getEmptyAdjacentLocations(1) == [0, 3]
  small_dinner.seatAlienAt(1,0)
  assert small_dinner.getEmptyAdjacentLocations(1) == [3]
  small_dinner.seatAlienAt(2,3)
  assert small_dinner.getEmptyAdjacentLocations(1) == []
  
def test_seating_dict(small_dinner):
  assert small_dinner.seatingDict() == {0:0, 1:0, 2:0, 3:0}
  small_dinner.seatAlienAt(3,0)
  assert small_dinner.seatingDict() == {0:3, 1:0, 2:0, 3:0}
  small_dinner.seatAlienAt(1,3)
  small_dinner.seatAlienAt(2,2)
  assert small_dinner.seatingDict() == {0:3, 1:0, 2:2, 3:1}