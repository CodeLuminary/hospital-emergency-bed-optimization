import simpy
import random
import numpy as np
#from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt

# Define the EmergencyUnit class
class EmergencyUnit:
    def __init__(self, env, num_beds, part=0.8):
        self.env = env
        self.beds = simpy.Resource(env, capacity=num_beds)
        self.waiting_times = []
        self.deferred_patients = 0
        self.treatment_time = [10,8,22,5,15,20,1,9,10,6,13,4,17,10, 19, 1, 7, 13,4,16]
        self.arrival_time = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
        self.mean_treatment_time = 0
        self.mean_arrival_time = 0
        self.patient_count = 0
        self.part = part

    def patient(self, patient_id, priority, treatment_duration):
        arrival_time = self.env.now
        bed_available = 1 if self.beds.count < self.beds.capacity else 0
        print(f"beds: {self.beds.count}")
        if priority == 0 and self.beds.count > (self.beds.capacity * self.part) and treatment_duration > (self.mean_treatment_time - self.mean_arrival_time):
            non_priority_waiting_time = self.mean_treatment_time - (((self.beds.capacity * self.part) - 1) * self.mean_arrival_time)
            #print(f"Waiting time: {non_priority_waiting_time}")
            #print(f"Waiting time2: {self.mean_treatment_time - self.mean_arrival_time}")
            if non_priority_waiting_time < 0:
              non_priority_waiting_time = self.mean_arrival_time
            yield self.env.timeout(non_priority_waiting_time)
        if priority == 1 or self.beds.count < (self.beds.capacity * self.part) or treatment_duration < (self.mean_treatment_time - self.mean_arrival_time):  # Admit if bed available or patient is priority
            with self.beds.request() as request:
                yield request
                waiting_time = self.env.now - arrival_time
                self.waiting_times.append(waiting_time)

                if waiting_time > 0 :
                    self.deferred_patients += 1

                # Simulate treatment time
                yield self.env.timeout(treatment_duration)

                self.mean_treatment_time = ((self.mean_treatment_time * self.patient_count) - self.treatment_time[patient_id])/(self.patient_count - 1)
                self.mean_arrival_time = ((self.mean_arrival_time*self.patient_count) - self.arrival_time[patient_id])/(self.patient_count - 1)
                self.patient_count -= 1


    def run(self, arrival_rate, treatment_time_mean, num_patients):
        for i in range(num_patients):
            priority = random.choice([0, 1])  # Binary flag: 1 for high priority, 0 for low

            #treatment_duration = random.expovariate(1.0 / treatment_time_mean)
            #arrr = random.expovariate(1.0 / arrival_rate)
            yield self.env.timeout(self.arrival_time[i])

            self.mean_treatment_time = ((self.mean_treatment_time * self.patient_count) + self.treatment_time[i])/(self.patient_count + 1)
            self.mean_arrival_time = ((self.mean_arrival_time*self.patient_count) + self.arrival_time[i])/(self.patient_count + 1)
            self.patient_count += 1

            print(f"duration {i}: {priority}: {self.env.now}: {self.treatment_time[i]}: {self.arrival_time[i]}")
            self.env.process(self.patient(i, priority, self.treatment_time[i]))

    def get_stats(self):
        print(self.waiting_times)
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