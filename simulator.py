import random
import copy

MAX_SIZE = 15
MAX_TIME = 20
MAX_CHANGES = 5

class Agent():
    """Class that represents an agent/party of certain size, certain utility for attending the event, and certain
    preferences for where to sit. The agent's id is iterative from 1 onward, and the agent's seats are those it
    currently has in its possession."""
    def __init__(self, id, size, value, pref="ordinary"):
        self.id = id
        self.size = size
        self.value = value
        self.pref = pref
        self.seats = []
        self.requests = []

    def __str__(self):
        return "Agent {}, size {}, value {}, and {} preferences, with {} seats".format(self.id, self.size, self.value, self.pref, len(self.seats))


class Request():
    """Class that represents an agent/party changing their group size at a certain time, and now desiring a minimum
    seat (id) for any trade to be valid. Assumption is that agents prefer lower id seats to higher id seats."""
    def __init__(self, agent_id, time, size, min_seat):
        self.agent_id = agent_id
        self.size = size
        self.time = time
        self.min_seat = min_seat

    def __str__(self):
        return "Request for agent {} with new size {} and minimum {} at time {}".format(self.agent_id, self.size, self.min_seat, self.time)


class Seat():
    """Class that represents a seat in the venue, identified by its seat, row, and section. The seat's occupancy will
    equal the id of whichever agent currently possesses it."""
    def __init__(self, seat, row, section, venue_size, occupied=0):
        self.venue_size = venue_size
        self.seat = seat
        self.row = row
        self.section = section
        self.occupied = occupied
        self.id = (self.section * self.venue_size["rows"] * self.venue_size["seats"]) + (
                    self.row * self.venue_size["seats"]) + self.seat

    def __str__(self):
        return "Seat ({}, {}, {}), occupied by {}".format(self.section, self.row, self.seat, self.occupied)


class History():
    """Class that makes a copy of the current state of the simulator, including all important variables, as a central
    record to be referenced to in the future."""
    def __init__(self, venue, agents, sizes, requests, cursors):
        self.venue = copy.deepcopy(venue)
        self.agents = copy.deepcopy(agents)
        self.sizes = copy.deepcopy(sizes)
        self.requests = copy.deepcopy(requests)
        self.cursors = copy.deepcopy(cursors)


class Cursor():
    """Class that represents a cursor, which iterates over the seats of the venue. Note that venue_size is a dictionary
    with keys for sizes of seats, rows, and sections. The cursor has a unique id representing the seat it is currently
    on, as well as identification by seat, row, and section."""
    def __init__(self, venue_size, new_id=0):
        self.venue_size = venue_size
        self.set_id(new_id)

    def __str__(self):
        return "Cursor ID {}, ({}, {}, {})".format(self.id, self.section, self.row, self.seat)

    def set_id(self, new_id):
        """Method that sets the cursor's new location using a new id."""
        self.id = new_id
        self.section = new_id // (self.venue_size["rows"] * self.venue_size["seats"])
        new_id %= (self.venue_size["rows"] * self.venue_size["seats"])
        self.row = new_id // self.venue_size["seats"]
        new_id %= self.venue_size["seats"]
        self.seat = new_id

    def set_location(self, position, type):
        """Method that sets a cursor's new location using a new seat, row, or section."""
        if position < 0:
            raise Exception("Not valid position.")
        if type == "seat":
            if position >= self.venue_size["seats"]:
                raise Exception("Seat out of range.")
            self.seat = position
        elif type == "row":
            if position >= self.venue_size["rows"]:
                raise Exception("Row out of range.")
            self.row = position
        else:
            if position >= self.venue_size["sections"]:
                raise Exception("Section out of range.")
            self.section = position
        self.id = (self.section * self.venue_size["rows"] * self.venue_size["seats"]) + (self.row * self.venue_size["seats"]) + self.seat



class Simulator():
    """Class that simulates the entire ticket purchasing process for the venue. It keeps track of time, of all the
    venue's seats, of all the agents involved, and of the existing agent party sizes."""
    def __init__(self, agents, venue_size, debug=False):
        self.time = 0
        self.venue = [[[Seat(i, j, k, venue_size) for i in range(venue_size["seats"])] for j in range(venue_size["rows"])] for k in range(venue_size["sections"])]
        # for section in self.venue:
        #     for row in section:
        #         for seat in row:
        #             print(str(seat))
        self.debug = debug
        self.venue_size = venue_size
        self.agents = agents
        self.sizes = {agent.size for agent in agents}
        self.requests = []
        self.requests_satisfied = []
        self.history = []

    def primary_market(self):
        """Method that allocates initial seating to all agents based on their relative utilities, sorting them into a
        queue and then ticketing them until the venue is full. At the end, records the first entry in the central
        history (index 0) to represent the initial allocation of seats."""
        queue = sorted(self.agents, key=lambda p: -p.value)

        # Create a cursor for each existing party size to keep track of the next open set of seats for that sized party
        cursors = {size: Cursor(self.venue_size, 0) for size in self.sizes}

        for agent in queue:
            if self.debug:
                for size, cursor in cursors.items():
                    print("{}: {}".format(size, cursor), end=", ")
                print()
                print(str(agent))

            # If the cursor is at the end of the venue, then there are no available seats left for the party
            if cursors[agent.size].section >= self.venue_size["sections"]:
                continue

            # This code helps introduce central tendencies for agents, so agents choose the tickets in their optimal
            # row to be as far away from the ends and the other agents in the row as possible.
            gap = self.calc_max_gap(cursors[agent.size], agent.size)
            if self.debug:
                print("Maximum gap is {}".format(gap))

            # Assigns the seats to the agent and records the agent as owning the seats
            for i in range(agent.size):
                cur_seat = self.venue[cursors[agent.size].section][cursors[agent.size].row][cursors[agent.size].seat + gap + i]

                if cur_seat.occupied != 0:
                    raise Exception("Agent {} tried to take seat {} but it was already occupied by Agent {}.".format(agent.id, cur_seat.id, cur_seat.occupied))
                cur_seat.occupied = agent.id
                agent.seats.append(cur_seat)
                # print(str(cur_seat))

            # Updates the cursors' positions to point to next sets of open seats
            for key, cursor in cursors.items():
                self.find_next_open(cursor, key)

        # Print final allocation information from primary market
        print("----ALLOCATION COMPLETE----")
        for agent in queue:
            print(str(agent))
        for section in self.venue:
            for row in section:
                for seat in row:
                    print(str(seat))
        for key, cursor in cursors.items():
            print("Size {} cursor at {}".format(key, cursor))

        self.cursors = cursors

        self.history.append(History(self.venue, self.agents, self.sizes, self.requests, self.cursors))

    def secondary_market(self, time):
        """Method which randomly introduces changes in agent party sizes as requests that the mechanisms should
        attempt to successfully satisfy. Also signals the beginning of a moment in time, so the time is recorded in the
        central simulator."""
        self.time = time
        num_changes = random.randint(1, MAX_CHANGES)
        changed_agents = random.sample(self.agents, num_changes)

        # Selects some random agents to have changes in party size
        for agent in changed_agents:
            try:
                test = agent.seats[0]
            except:
                print("Not currently allocated")
                continue
            change = random.randint(1, 4)
            negative = random.randint(0, 1)
            min_seat = self.venue_size["sections"] * self.venue_size["rows"] * self.venue_size["seats"]
            if negative == 0:
                change = -change
                min_seat = agent.seats[-1].id

            # Represents these changes as requests under the agents they belong to
            request = Request(agent.id, time, max(1, agent.size + change), min_seat)
            agent.requests.append(request)
            self.requests.append(request)
            print("Requesting change of {} for agent {} currently in seats {} to {}, {} total to {} new, and min seat {}, at time {}".format(change, agent.id, agent.seats[0].id, agent.seats[-1].id, len(agent.seats), max(1, agent.size + change), min_seat, time))

    def check_requests(self):
        """Method that determines which requests have been successfully granted, thus deleting those from the central
        list of requests and appending to the central list of satisfied requests. Also signifies the end of the moment
        in time, so a new entry is recorded in the simulator history."""
        satisfied = []
        for index, request in enumerate(self.requests):
            # Note that we must offset by 1 because agent id's start at 1 and not 0
            if len(self.agents[request.agent_id - 1].seats) == request.size:
                print("Agent {} has size {} that matches request size {}".format(self.agents[request.agent_id - 1].id, len(self.agents[request.agent_id - 1].seats), request.size))
                if self.agents[request.agent_id - 1].seats[-1].id > request.min_seat:
                    raise Exception("Minimum seat was {}, but allocated seat {} instead.".format(request.min_seat, self.agents[request.agent_id - 1].seats[-1].id))
                else:
                    print("Request successfully granted for agent {}, new seats {} to {}".format(request.agent_id, self.agents[request.agent_id - 1].seats[0].id, self.agents[request.agent_id - 1].seats[-1].id))
                    self.requests_satisfied.append(request)
                    satisfied.append(index)
                    self.agents[request.agent_id - 1].requests.clear()
            else:
                print("Request still pending for agent {} with current size {} and seat {}, new size {}".format(self.agents[request.agent_id - 1].id, len(self.agents[request.agent_id - 1].seats), self.agents[request.agent_id - 1].seats[0].id, request.size))

        for index in list(reversed(satisfied)):
            self.requests.pop(index)

        self.history.append(History(self.venue, self.agents, self.sizes, self.requests, self.cursors))

    def final_calcs(self):
        num_alloc = 0
        for agent in self.agents:
            print(str(agent))
            if len(agent.seats) > 0:
                num_alloc += 1

        for section in self.venue:
            for row in section:
                for seat in row:
                    print(str(seat))

        print("In total, {} agents allocated, {} agents unallocated, {} requests satisfied".format(num_alloc, len(self.agents) - num_alloc, len(self.requests_satisfied)))


    def calc_max_gap(self, cursor, size):
        """Method that calculates the maximum gap the current sized party could leave in its optimal row between itself
        and the ends/other agents"""
        if self.debug:
            print("Calculating max gap...")
            print("Start of open space is seat {}".format(cursor.seat))
        end = cursor.seat

        while end < self.venue_size["seats"]:
            if self.venue[cursor.section][cursor.row][end].occupied != 0:
                break
            end += 1

        if self.debug:
            print("End of open space is seat {}".format(end))

        total_space = end - cursor.seat - size
        return total_space // 2

    def find_next_open(self, cursor, size):
        """Method that finds the next open set of seats of the appropriate size to move the cursor to"""
        count = 0
        while count < size:
            try:
                cur_seat = self.venue[cursor.section][cursor.row][cursor.seat]
            except:
                print("Venue capacity reached for size {}".format(size))
                return

            if cursor.seat < count:
                count = 0
            if cur_seat.occupied == 0:
                count += 1
            else:
                count = 0
            cursor.set_id(cursor.id + 1)

        cursor.set_id(cursor.id - size)

