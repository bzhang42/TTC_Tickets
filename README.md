# TTC Tickets
CS 136 Final Project by Aditya Dhar, Bill Zhang, David Zhu

Mechanism and simulator for trading sets of event tickets between parties to make the secondary market for event 
ticketing more efficient. Utilizes Top-Trading-Cycles (TTC) mechanism to detect and execute trades in real time.

## Organization
The project is organized into the following:

* main.py
* simulator.py

See below for details on each file

### main

This file contains the execution of the simulator and mechanism(s). It will generate a random number of agents,
which are modeled as parties of a certain size, a certain collective utility for attending the event, and ultimately
a certain set of seats allocated to them by the simulator. This file also constructs a model for a venue with a set
number of sections, rows in a section, and seats in a row, indexed from closest (smallest) to farthest (largest) from
the stage.

We initially draw the group sizes and group utilities from discrete uniform distributions, but this can be altered
to reflect different distributions as desired.

### simulator

This file contains the simulator, as well as the classes for the relevant objects in the simulation. These classes
include Agent (to represent different parties of people), Request (to represent changes of plans), Seat (to represent a
seat, its location, and its occupancy), Cursor (to point to locations within the venue), and Simulator (which simulates 
primary market allocation and secondary market demand).

There are a few nuances to make note of for the simulator and its handling of primary market allocation:
* The simulator will always allocate adjacent seats on the same row to a party. We are operating under the assumption
that parties want to be in the same row as each other, rather than in a block or some other arrangement.
* The simulator will exhibit central tendencies, assigning to a party the seats in a row that are farthest from the
ends and from other parties. This is to reflect the tendency for consumers to select ticket spots in the same way.
* The simulator will assume all agents exhibit normal preferences, meaning they prefer lower indexed seats (closer to
the stage) than higher indexed seats (farther from the stage).

There are also a few nuances to make note of for the simulator's handling of secondary market demands (changes of plans):
* The simulator proceeds through a set number of units in time, and at each moment in time there is a random chance of 
requests and additional agents appearing.
* The simulator will limit changes in party size to a certain range (by default, uniform from -2 to 2) to reflect real
consumer tendencies.
* The simulator will assume that if a party adds people, it is now fine with any set of seats in the venue (minimum 
seat is thus the seat at the last index). If a party drops people, it is now fine only with sets of seats indexed 
in front of it within the venue. For now, we assume no monetary alternatives are in play.
* The simulator will keep track of which requests are satisfied and which are not after each moment in time. A satisfied
request is one where the number of seats given is equal to the party size, and the seats are all better than the minimum 
seat. Finally, the seats must all still be adjacent (consecutive in the same row).