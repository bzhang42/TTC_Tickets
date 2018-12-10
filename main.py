from simulator import *

if __name__ == '__main__':
    agents = []

    # Generate random agent sizes and utilities based on seed (default: 1)
    random.seed(1)

    # Create agents 1-40 with max party size and utility from 0 to 100
    for i in range(1, 41):
        agents.append(Agent(i, random.randint(1, MAX_SIZE), random.randint(0, 100)))

    print("----ALL AGENTS----")
    for index, agent in enumerate(agents):
        print("Agent {} at index {}".format(agent, index))

    # Run the simulation for primary market
    print("----RUNNING SIMULATION----")
    sim = Simulator(agents, {"seats": 20, "rows": 5, "sections": 3})

    print("----PRIMARY MARKET ALLOCATION----")
    sim.primary_market()

    print("----SECONDARY MARKET PROGRESSION----")
    # Proceed through certain number of intervals in time
    for time in range(1, MAX_TIME):
        print("----TIME {}----".format(time))
        # Create random changes in plans and party sizes
        sim.secondary_market(time)

        # Insert mechanism code here

        # Check which requests have been satisfied and delete them from the list
        print("----CHECKING REQUESTS----")
        sim.check_requests()