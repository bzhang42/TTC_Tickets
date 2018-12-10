from simulator import *
import copy

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
			if openSeats[other.id] >= size and other.seats[-1].id < min_seat:
				prefs[agent].append(other)
		prefs[agent].sort(key= lambda p: p.seats[-1].id)

	return prefs

def filterAgents(sim, satisfied):
	curList = genPrefLists(sim)
	for agent in satisfied:
		del curList[agent]
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

	for agent in curList:
		pref = curList[agent]
		print("")
		print("Preferences of")
		print(agent)
		print("are")
		for other in pref:
			print(other)
	return curList

def doDFS(prefs, cur):
	tradeList = []
	while cur not in tradeList:
		tradeList.append(cur)
		cur = prefs[cur][0]
	while tradeList[0] != cur:
		tradeList.pop(0)
	return tradeList

def doTrade(sim, tradeList):
	oldSeats = {}
	for agent in tradeList:
		oldSeats[agent] = copy.deepcopy(agent.seats)
	for i in range(len(tradeList)):
		cur = tradeList[i]
		if i == len(tradeList) - 1:
			want = tradeList[0]
		else:
			want = tradeList[i+1]

		cur.seats.clear()
		prev_cursor = Cursor(sim.venue_size, oldSeats[want][0].id - 1)
		while sim.venue[prev_cursor.section][prev_cursor.row][prev_cursor.seat].occupied == 0 and oldSeats[want][0].row == prev_cursor.row:
			prev_cursor.set_id(prev_cursor.id - 1)
		prev_cursor.set_id(prev_cursor.id + 1)

		for oldSeat in oldSeats[want]:
			if sim.venue[oldSeat.section][oldSeat.row][oldSeat.seat].occupied == want.id:
				sim.venue[oldSeat.section][oldSeat.row][oldSeat.seat].occupied = 0

		if len(cur.requests) > 0:
			numSeats = cur.requests[-1].size
		else:
			numSeats = len(oldSeats[cur])
		for j in range(numSeats):
			cur_seat = sim.venue[prev_cursor.section][prev_cursor.row][prev_cursor.seat]
			cur_seat.occupied = cur.id
			cur.seats.append(cur_seat)
			prev_cursor.set_id(prev_cursor.id + 1)
		cur.size = numSeats

def doTTC(sim):
	satisfied = []
	tradesExecuted = 0
	fPrefs = filterAgents(sim, satisfied)
	while len(fPrefs) > 0:
		tradeList = []
		for curAgent in fPrefs:
			tradeList = doDFS(fPrefs, curAgent)
			break
		print("")
		print("Executing trade")
		tradesExecuted += 1
		for agent in tradeList:
			print(agent)

		doTrade(sim, tradeList)

		for agent in tradeList:
			satisfied.append(agent)
		fPrefs = filterAgents(sim, satisfied)
	print(str(tradesExecuted) + " trade(s) executed this time period")
	return tradesExecuted
