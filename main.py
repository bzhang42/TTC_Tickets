from simulator import *

if __name__ == '__main__':
    agents = []

    # Generate random agent sizes and utilities based on seed (default: 1)
    random.seed(1)

    # Create agents 1-40 with max party size and utility from 0 to 100
    for i in range(1, 41):
        agents.append(Agent(i, random.randint(1, MAX_SIZE), random.randint(0, 100)))

    print("----ALL AGENTS----")
    for agent in agents:
        print(str(agent))

    # Run the simulation for primary market
    print("----RUNNING SIMULATION----")
    sim = Simulator(agents, {"seats": 20, "rows": 5, "sections": 3})

    print("----CHANGES START NOW----")
    # Simulates a certain period of time where random changes in party size occur the random agents
    for time in range(1, MAX_TIME):
        print("Time {}".format(time))
        sim.time = time
        num_changes = random.randint(1, 5)
        changed_agents = random.sample(sim.agents, num_changes)

        # Selects some random agents to have changes in party size
        for agent in changed_agents:
            change = random.randint(1, 2)
            negative = random.randint(0, 1)
            min_seat = sim.venue_size["sections"] * sim.venue_size["rows"] * sim.venue_size["seats"]
            if negative == 0:
                change = -change
                try:
                    min_seat = agent.seats[0].id
                except:
                    print("Not currently allocated")

            # Represents these changes as requests under the agents they belong to
            agent.requests.append(Request(agent.id, time, max(1, agent.size + change), min_seat))
            print("Requesting change of {} for agent currently in seat {}".format(change, agent.seats[0].id))
            print(agent.requests[-1])
