from simulator import *

def calcOpenSeats(sim):
	openSeats = {}
	for agent in sim.agents:
		if len(agent.seats) == 0:
			openSeats[agent.id] = 0
		else:
			lSeat = agent.seats[0]
			rSeat = agent.seats[-1]
			openAdj = 0
			cursor = Cursor(sim.venue_size, lSeat.id - 1)
			curSeat = sim.venue[cursor.section][cursor.row][cursor.seat]
			while curSeat.occupied == 0 and curSeat.row == lSeat.row:
				openAdj += 1
				cursor = Cursor(sim.venue_size, curSeat.id - 1)
				if cursor.section < 0:
					break
				curSeat = sim.venue[cursor.section][cursor.row][cursor.seat]
			cursor = Cursor(sim.venue_size, rSeat.id + 1)
			curSeat = sim.venue[cursor.section][cursor.row][cursor.seat]
			while curSeat.occupied == 0 and curSeat.row == rSeat.row:
				openAdj += 1
				cursor.set_id(cursor.id + 1)
				if cursor.section >= sim.venue_size["sections"]:
					break
				curSeat = sim.venue[cursor.section][cursor.row][cursor.seat]
			openSeats[agent.id] = len(agent.seats) + openAdj
	print(openSeats)
