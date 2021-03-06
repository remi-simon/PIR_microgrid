import numpy as np
import os 
from numpy.random import randint 

"""
Class for the Charging Station
Some fields must be completed by students

"""

class ChargingStation:

	def __init__(self, path_to_data_folder):

		self.path_to_data_folder = path_to_data_folder
		self.n_data = 10
		self.dt = 0.5

		self.efficiency = 0.95

		self.scenario = {}
		self.bill = np.zeros(48)
		self.load = np.zeros(48)
		self.battery_stock = {"slow" : np.zeros(49), "fast" : np.zeros(49)}
		self.nb_fast = 2
		self.nb_slow = 2
		
		self.information={"my_buy_price" : np.zeros(49), "grid_buy_price" : np.zeros(49),
                          "my_sell_price" : np.zeros(49), "grid_sell_price" : np.zeros(49)}

	def flexible(self,time):

		cmax = self.scenario["load_charging_station_capacity"][0,time] # Available Capacity   
		pmax = self.scenario["load_charging_station_capacity"][1,time] # Available Power
		soc = self.scenario["load_charging_station_capacity"][2,time]  # State Of Charge of the vehicles

		
		self.nb_slow = int((pmax%22)/3)
		self.nb_fast = cmax/40 - self.nb_slow

		p_max = {"slow" : 3*self.nb_slow, "fast" : 22*self.nb_fast}
		c_max = {"slow" : 40*self.nb_slow, "fast" : 40*self.nb_fast}

		load_battery = {"slow" : 0, "fast" : 0}
		my_buy_price = self.information["my_buy_price"][time]
		my_sell_price = self.information["my_sell_price"][time]
		grid_buy_price = self.information["grid_buy_price"][time]
		grid_sell_price = self.information["my_sell_price"][time]


		## to be modified
		
		load_battery["fast"] = 0
		load_battery["slow"] = 0
		
		if time < 4  :
			load_battery["fast"] = 44

		if time < 11  :
			load_battery["slow"] = 6
				
		if time >= 12 and time<18 and self.battery_stock["fast"][time]>(10*self.nb_fast + 13/self.efficiency):
			load_battery["fast"] = -p_max["fast"]
		
		if time >= 12 and time<18 and self.battery_stock["slow"][time]>(10*self.nb_slow + 2/ self.efficiency):
			load_battery["slow"] = -p_max["slow"]

			
		if time > 36 and time<40 :
			for speed in ["slow","fast"]:
				load_battery[speed] = p_max[speed]
		
		if time > 40:
			for speed in ["slow","fast"]:
				load_battery[speed] = -p_max[speed]
			
		return load_battery


	def update_batterie_stock(self, time, load_battery):
		
		cmax = self.scenario["load_charging_station_capacity"][0,time] # Available Capacity   
		pmax = self.scenario["load_charging_station_capacity"][1,time] # Available Power
		soc = self.scenario["load_charging_station_capacity"][2,time]  # State Of Charge of the vehicles
		
		self.nb_slow = int((pmax%22)/3)
		self.nb_fast = cmax/40 - self.nb_slow
		
		nb={"slow" : self.nb_slow, "fast" : self.nb_fast}
		p_max = {"slow" : 3*self.nb_slow, "fast" : 22*self.nb_fast}
		c_max = {"slow" : 40*self.nb_slow, "fast" : 40*self.nb_fast}

		
		for speed in ["slow","fast"] :
			if abs(load_battery[speed]) >= p_max[speed] :
				load_battery[speed] = p_max[speed]*np.sign(load_battery[speed])

		new_stock = { "slow" : self.battery_stock["slow"][time] + (self.efficiency*max(0,load_battery["slow"])+min(0,load_battery["slow"])/self.efficiency)*self.dt + soc, 
                      "fast" : self.battery_stock["fast"][time] + (self.efficiency*max(0,load_battery["fast"])+min(0,load_battery["fast"])/self.efficiency)*self.dt }

		if time>12 and time<18:
			speed = "slow"
			if nb[speed]*10 > new_stock[speed] :
					self.bill[time] += 5
			
			speed="fast"
			if nb[speed]*10 > new_stock[speed] :
				load_battery[speed]=nb[speed]*22
				new_stock[speed]+= 22*nb[speed]*self.dt
				
				
		for speed in ["slow","fast"] :
			if new_stock[speed] < 0:
				load_battery[speed] = -(self.battery_stock[speed][time]  + soc)/(self.efficiency*self.dt)
				new_stock[speed] = 0
			
			elif new_stock[speed] > c_max[speed]:
				load_battery[speed] = (c_max[speed] - self.battery_stock[speed][time] ) / (self.efficiency*self.dt)
				
				new_stock[speed] = c_max[speed]
				
		for speed in ["slow","fast"] :
			if abs(load_battery[speed]) >= p_max[speed] :
				load_battery[speed] = p_max[speed]*np.sign(load_battery[speed])
				
		for speed in ["slow","fast"] :
			self.battery_stock[speed][time+1]=new_stock[speed]
		
		return load_battery
		


	def compute_load(self,time):

		load_battery = self.flexible(time)
		load = self.update_batterie_stock(time, load_battery)
		self.load[time] = load["slow"] + load["fast"]


	def draw_random_scenario(self):

		#tableau NPY
		test_load_charging_station_capacity = np.load(os.path.join(self.path_to_data_folder, "charging-station","test_capacity_power_soc_charging-station.npy"))
		self.scenario["load_charging_station_capacity"]= test_load_charging_station_capacity [randint(self.n_data),:,:] 

		self.bill = np.zeros(48)
		self.load = np.zeros(48)
		self.battery_stock = {"slow" : np.zeros(49), "fast" : np.zeros(49)}
		self.nb_fast = 2
		self.nb_slow = 2


"""
Test your code before submition

"""

if __name__ == '__main__':

	current_path = os.path.dirname(os.path.realpath(__file__))
	path_to_data = os.path.join(current_path, "..", "data")
	charging_station = ChargingStation(path_to_data)

	charging_station.draw_random_scenario()
	charging_station.compute_load(0)
	
	# for i in range(1000):
	# 	charging_station.draw_random_scenario()
	# 	for time in range (48):
	# 		charging_station.compute_load(time)
	# 		stock = charging_station.battery_stock["slow"][time] + charging_station.battery_stock["fast"][time]
	# 		if stock<0 : print (stock)
		
	
	for time in range (48):
		charging_station.compute_load(time)
		stock = charging_station.battery_stock["slow"][time] + charging_station.battery_stock["fast"][time]
		
		if time<19 :
			print (str(round(charging_station.load[time],1))+" | " + str(round(stock,1)))
			
		if time == 20 : print ("***")
	
		if time > 36 :
			print (str(round(charging_station.load[time],1)) +" | " + str(round(stock,1)))

	print("Test passed, ready to submit !")