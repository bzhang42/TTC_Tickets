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
	print("Open seats for each agent are")
	print(openSeats)
	return openSeats

def genPrefLists(sim):
	openSeats = calcOpenSeats(sim)
	prefs = {}
	for agent in sim.agents:
		prefs[agent] = []
		if len(agent.seats) == 0:
			continue
		size = agent.size
		min_seat = agent.seats[-1].id
		if len(agent.requests) > 0:
			size = agent.requests[-1].size
			min_seat = agent.requests[-1].min_seat
		for other in sim.agents:
			#if agent.id == other.id:
			#	continue
			if openSeats[other.id] >= size and other.seats[-1].id < min_seat:
				prefs[agent].append(other)
		prefs[agent].sort(key= lambda p: p.seats[-1].id)

	for agent in prefs:
		pref = prefs[agent]
		print("")
		print(agent)
		for other in pref:
			print(other) 
	#print(prefs)
	return prefs

def filterAgents(sim):
	curList = genPrefLists(sim)
	changed = True
	toDelete = []
	while changed:
		changed = False
		for agent in curList:
			prefs = curList[agent]
			found = False
			for other in prefs:
				if other in curList:
					found = True
				else:
					curList[agent].remove(other)
					changed = True
			if not found:
				toDelete.append(agent)
		for agent in toDelete:
			del curList[agent]
			changed = True
		toDelete.clear()
		print("cleared")

	for agent in curList:
		pref = curList[agent]
		print("filtered")
		print(agent)
		for other in pref:
			print(other) 
	return curList


# first step is to iteratively remove all agents with empty pref lists from the pool
# once all of those agents are removed, run TTC
def doTTC(sim):
	fPrefs = filterAgents(sim)
	





