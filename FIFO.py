import simpy
import random
import numpy as np
#from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt

# Define the EmergencyUnit class
class EmergencyUnit:
    def __init__(self, env, num_beds):
        self.env = env
        self.beds = simpy.Resource(env, capacity=num_beds)
        self.treatment_time = [10,8,22,5,15,20,1,9,10,6,13,4,17,10, 19, 1, 7, 13,4,16]
        self.arrival_time = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
        self.waiting_times = []
        self.deferred_patients = 0


    def patient(self, patient_id, treatment_duration):
        arrival_time = self.env.now
        #bed_available = 1 if self.beds.count < self.beds.capacity else 0
        print(f"Beds count: {self.beds.count}")
        #if bed_available:  # Admit if bed available or patient is priority
        with self.beds.request() as request:
            yield request
            waiting_time = self.env.now - arrival_time
            self.waiting_times.append(waiting_time)
            if waiting_time > 0 :
              self.deferred_patients += 1

            # Simulate treatment time
            yield self.env.timeout(treatment_duration)
        #else:
            #self.deferred_patients += 1

    def run(self, arrival_rate, treatment_time_mean, num_patients):
        for i in range(num_patients):
            #priority = random.choice([0, 1])  # Binary flag: 1 for high priority, 0 for low

            #treatment_duration = random.expovariate(1.0 / treatment_time_mean)
            arrr = random.expovariate(1.0 / arrival_rate)
            yield self.env.timeout(self.arrival_time[i])
            print(f"duration {i}: {self.env.now}: {self.treatment_time[i]}")
            self.env.process(self.patient(i, self.treatment_time[i]))

    def get_stats(self):
        print(f"Patients waiting time: {self.waiting_times}")
        plt.plot(self.waiting_times)
        avg_waiting_time = sum(self.waiting_times) / len(self.waiting_times) if self.waiting_times else 0
        return {
            'avg_waiting_time': avg_waiting_time,
            'deferred_patients': self.deferred_patients
        }

# Define simulation wrapper
def simulate_bed_allocation(num_beds, arrival_rate, treatment_time_mean, num_patients, simulation_time):
    env = simpy.Environment()
    emergency_unit = EmergencyUnit(env, num_beds)
    env.process(emergency_unit.run(arrival_rate, treatment_time_mean, num_patients))
    env.run(until=simulation_time)
    return emergency_unit.get_stats()

# Run a quick test of the simulation
#if _name_ == "_main_":
num_beds = 5
arrival_rate = 5
treatment_time_mean = 10
num_patients = 20
simulation_time = 1000

stats = simulate_bed_allocation(num_beds, arrival_rate, treatment_time_mean, num_patients, simulation_time)
print(f"Average waiting time: {stats['avg_waiting_time']}")
print(f"Number of patients that waited: {stats['deferred_patients']}")