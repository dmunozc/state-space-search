import enum


class Alien(enum.Enum):
    """Enum to differentiate types of aliens."""

    host = 1
    guest = 2


class Bar:
    """Defines all the rules for the bar.  

    This class handles the internal representation of the seating bar
    (for a rectangular table).
    """

    def __init__(self, number_of_guests, init_seating=None):
        if init_seating:
            self.seats = init_seating
        else:
            self.seats = [0] * number_of_guests
        self.seated_count = 0

    def seat_alien_at(self, alien, location):
        self.seats[location] = alien
        self.seated_count += 1

    def unseat_location(self, location):
        """Returns the unseated alien, if any."""
        alien = self.seats[location]
        self.seats[location] = 0
        self.seated_count -= 1
        return alien

    def alien_at_location(self, location):
        return self.seats[location]

    def _seats_per_row(self):
        return len(self.seats) // 2

    def get_adjacent(self, location):
        """Returns a list of the adjacent locations.

        An adjacent locations is defined for a rectangular table as:
          Across
          To the left
          To the right.
        """
        seats_per_row = self._seats_per_row()
        if location < seats_per_row:
            # If I am at a corner, only two adjacent places.
            if location == 0:
                return [1, seats_per_row]
            if location == seats_per_row - 1:
                return [location - 1, seats_per_row * 2 - 1]
            return [location - 1, location + 1, seats_per_row + location]
        else:
            # If I am at a corner, only two adjacent places.
            if location == seats_per_row:
                return [location + 1, 0]
            if location == seats_per_row * 2 - 1:
                return [location - 1, seats_per_row - 1]
            return [location - 1, location + 1, location - seats_per_row]

    def alien_location(self, alien):
        """Returns the table location of a specific alien."""
        for i in range(len(self.seats)):
            if self.seats[i] == alien:
                return i
        return -1

    def _get_seating(self, start, multiplier):
        return self.seats[start : self._seats_per_row() * multiplier]

    def top_seating(self):
        return self._get_seating(0, 1)

    def bottom_seating(self):
        return self._get_seating(self._seats_per_row(), 2)

    def seating_full(self):
        return self.seated_count == len(self.seats)

    def location_empty(self, location):
        return self.seats[location] == 0


class Dinner:
    """Defines all the rules for the dinner situation.

      This class is the main interface to the bar. It measures the level of
      satisfaction of the current seating.
      """

    def __init__(self, number_of_guests, preference_matrix, init_seating=None, safe=False):
        self.number_of_guests = number_of_guests
        assert len(preference_matrix) == number_of_guests
        assert len(preference_matrix[0]) == number_of_guests
        self.preference_matrix = preference_matrix
        if init_seating:
            assert len(init_seating) == number_of_guests
        self.table = Bar(number_of_guests, init_seating)
        self.aliens_seated = []
        self.aliens_not_seated = [i + 1 for i in range(number_of_guests)]
        self.allRoles = {}
        for i in range(number_of_guests):
            if i < number_of_guests / 2:
                self.allRoles[i + 1] = Alien.host
            else:
                self.allRoles[i + 1] = Alien.guest
        self.safe = safe

    def _valid_alien(self, alien):
        return self.number_of_guests >= alien >= 0

    def _valid_location(self, location):
        if location >= self.number_of_guests or location < 0:
            return False
        return True

    def get_adjacent_locations(self, location):
        return self.table.get_adjacent(location)

    def get_empty_adjacent_locations(self, location):
        adj = self.table.get_adjacent(location)
        return [loc for loc in adj if self.alien_at_location(loc) == 0]

    def role(self, alien):
        if self.safe:
            assert self._valid_alien(alien)
        return self.allRoles[alien]

    def preference(self, alien1, alien2):
        if self.safe:
            assert self._valid_alien(alien1)
            assert self._valid_alien(alien2)
        return self.preference_matrix[alien1 - 1][alien2 - 1]

    def seat_alien_at(self, alien, location):
        if self.safe:
            assert self._valid_alien(alien)
            assert self._valid_location(location)
            assert self.table.location_empty(location)
        self.table.seat_alien_at(alien, location)
        self.aliens_seated.append(alien)
        self.aliens_not_seated.remove(alien)
        if self.safe:
            assert len(self.aliens_not_seated) + len(self.aliens_seated) == self.number_of_guests

    def unseat_alien(self, alien):
        if self.safe:
            assert self._valid_alien(alien)
        location = self.table.alien_location(alien)
        if self.safe:
            assert location >= 0
        self.table.unseat_location(location)
        self.aliens_seated.remove(alien)
        self.aliens_not_seated.append(alien)
        if self.safe:
            assert len(self.aliens_not_seated) + len(self.aliens_seated) == self.number_of_guests
        return location

    def unseat_location(self, location):
        if self.safe:
            assert self._valid_location(location)
            assert self.table.location_empty(location) == False
        alien = self.table.unseat_location(location)
        self.aliens_seated.remove(alien)
        self.aliens_not_seated.append(alien)
        if self.safe:
            assert len(self.aliens_not_seated) + len(self.aliens_seated) == self.number_of_guests
        return alien

    def swap_aliens(self, alien1, alien2):
        location1 = self.unseat_alien(alien1)
        location2 = self.unseat_alien(alien2)
        self.seat_alien_at(alien1, location2)
        self.seat_alien_at(alien2, location1)

    def alien_at_location(self, location):
        return self.table.alien_at_location(location)

    def bar_full(self):
        return self.table.seating_full()

    # returns a dictionary get values location:alien
    def current_seating(self):
        return self.table.seats

    def seating_dict(self):
        res = {}
        for i in range(self.number_of_guests):
            res[i] = self.alien_at_location(i)
        return res

    def location_score(self, loc):
        """Return the score of the current location only"""
        if self.safe:
            assert self._valid_location(loc)
        score = 0
        top = self.table.top_seating()
        bottom = self.table.bottom_seating()
        seats_per_row = self.table._seats_per_row()
        if loc < seats_per_row:
            seating = top
            if bottom[loc] > 0:
                if self.role(top[loc]) != self.role(bottom[loc]):
                    score += 2
                score += self.preference(top[loc], bottom[loc])
                score += self.preference(bottom[loc], top[loc])
        else:
            seating = bottom
            loc -= seats_per_row
            if top[loc] > 0:
                if self.role(top[loc]) != self.role(bottom[loc]):
                    score += 2
                score += self.preference(top[loc], bottom[loc])
                score += self.preference(bottom[loc], top[loc])
        if loc < seats_per_row - 1:
            if seating[loc + 1] > 0:
                if self.role(seating[loc]) != self.role(seating[loc + 1]):
                    score += 1
                score += self.preference(seating[loc], seating[loc + 1])
                score += self.preference(seating[loc + 1], seating[loc])
        if loc > 0:
            if seating[loc - 1] > 0:
                if self.role(seating[loc]) != self.role(seating[loc - 1]):
                    score += 1
                score += self.preference(seating[loc], seating[loc - 1])
                score += self.preference(seating[loc - 1], seating[loc])

        return score

    def bar_score(self):
        """Return the score of the whole bar"""
        score = 0
        top = self.table.top_seating()
        bottom = self.table.bottom_seating()
        for row in [top, bottom]:
            for i in range(len(row) - 1):
                if row[i] > 0 and row[i + 1] > 0:
                    if self.role(row[i]) != self.role(row[i + 1]):
                        score += 1
                    score += self.preference(row[i], row[i + 1])
                    score += self.preference(row[i + 1], row[i])
        for i in range(len(top)):
            if top[i] > 0 and bottom[i] > 0:
                if self.role(top[i]) != self.role(bottom[i]):
                    score += 2
                score += self.preference(top[i], bottom[i])
                score += self.preference(bottom[i], top[i])
        return score
