import csv
import json
import random

class Tournament:
    class Team:
        def __init__(self, sponsor, budget):
            self.sponsor = sponsor      # Team sponsor (car brand)
            self.budget = budget        # Team sponsor budget
            self.inventory = []         # Team car inventory
            self.active = True          # Team active status
            self.wins = 0               # Number of wins
            self.losses = 0             # Number of losses
            self.total_score = 0        # Total score of the team
            self.record = []            # Win-loss record
            self.total_car = 0          # Total number of cars purchased
            
        def __str__(self):
            return f"Team {self.sponsor}, Budget: {self.budget}, Wins: {self.wins}, Losses: {self.losses}, Total Score: {self.total_score}, Total Car: {self.total_car}"
        
        def __repr__(self):
            return self.__str__()
        
    def __init__(self, config_path=None):
        config_path = "./data/config.json"
        # Tournament configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        self.name = config["name"]
        self.data_path = config["path"]
        self.nteams = config.get("nteams", 16)
        self.default_low = config["default_low"]
        self.default_high = config["default_high"]
        self.default_incr = config["default_incr"]
        
        # Sanity checks
        if not isinstance(self.nteams, int):
            raise ValueError("The number of teams must be an integer.")
        assert self.nteams > 0, "The number of teams must be positive."
        assert (self.nteams & (self.nteams - 1)) == 0, "The number of teams must be a power of 2."
        
        self.car_data = self._load_car_data()
        self.teams = []
        self.champion = None
        self.sponsor_budgets = {}
        
        
    def __repr__(self):
        return f"Tournament {self.name}, Teams: {len(self.teams)}, Champion: {self.champion}"
    
    def _load_car_data(self):
        with open(self.data_path, 'r') as f:
            reader = csv.DictReader(f)
            car_data = list(reader)
        return car_data
            
    def generate_sponsors(self, sponsor_list=None, low=None, high=None, incr=None, fixed_budget=None):
        # Set budget range
        low = low or self.default_low
        high = high or self.default_high
        incr = incr or self.default_incr
        
        makes = list(set(car["Make"] for car in self.car_data)) 
        sponsors = []

        if sponsor_list is not None:
            if len(sponsor_list) > self.nteams:
                raise ValueError("The number of sponsors exceeds the number of teams.")
            sponsors = sponsor_list[:]
            remaining = self.nteams - len(sponsors)
            available = list(set(makes) - set(sponsors))
            random.shuffle(available)
            sponsors.extend(available[:remaining])
        else:
            sponsors = random.sample(makes, min(self.nteams, len(makes)))
        # Fill in remaining slots randomly if needed
        while len(sponsors) < self.nteams:
            sponsors.append(random.choice(makes))

        self.sponsor_info = []
        for sponsor in sponsors:
            if fixed_budget is not None:
                if not (low <= fixed_budget <= high):
                    raise ValueError(f"Fixed budget must be between {low} and {high}.")
                budget = fixed_budget
            else:
                budget = random.randrange(low, high+1, incr)
            
            self.sponsor_info.append({"sponsor": sponsor, "budget": budget})

    def generate_teams(self):
        self.teams = []
        for info in self.sponsor_info:
            team = self.Team(info["sponsor"], info["budget"])
            self.teams.append(team)
    
    def buy_cars(self):
        for team in self.teams:
            self._purchase_inventory(team)

    def _purchase_inventory(self, team):
        # Purchase strategy: buy sponsor's most fuel-efficient cars first
        sponsor_cars = [car for car in self.car_data if car["Make"] == team.sponsor]

        for car in sponsor_cars:
            car["Price"] = float(car["Price"])
            car["MPG-H"] = float(car["MPG-H"])

        sponsor_cars.sort(key=lambda x: (-x["MPG-H"], x["Price"]))
        for car in sponsor_cars:
            price = car["Price"]
            #if car not in team.inventory and team.budget >= price:
            if team.budget >= price:
                team.inventory.append(car)
                team.budget -= price
                team.total_car += 1

    
    def hold_event(self):
        # Simulate a tournament event
        round_number = 1
        active_teams = [team for team in self.teams if team.active]
        while len(active_teams) > 1:
            next_event = []
            print(f"Round {round_number}")
            for i in range(0, len(active_teams), 2):
                team1 = active_teams[i]
                team2 = active_teams[i+1]
                score1 = sum(car["MPG-H"] for car in team1.inventory)
                score2 = sum(car["MPG-H"] for car in team2.inventory)

                # Determine winner
                if score1 > score2:
                    winner, loser = team1, team2
                elif score2 > score1:
                    winner, loser = team2, team1
                else:
                    print(f"It's a draw between {team1.sponsor} and {team2.sponsor}.")
                    winner = random.choice([team1, team2])
                    loser = team2 if winner == team1 else team1
                    print(f"Winner by random choice: {winner.sponsor}")
                # Update scores and records
                winner.wins += 1
                loser.losses += 1
                team1.total_score += score1
                team2.total_score += score2
                winner.record.append('W ')  
                loser.record.append('L ')
                winner.budget += 50000
                winner.active = True
                loser.active = False
                self._purchase_inventory(winner)
                next_event.append(winner)
                print(f"{winner.sponsor} wins with a score of {max(score1, score2)} against {loser.sponsor} with a score of {min(score1, score2)}.")
            active_teams = next_event
            round_number += 1
        self.champion = active_teams[0] if active_teams else None
        print(f"Tournament Champion: {self.champion}")


   
    
    def show_win_record(self):
        # Show win-loss records of all teams
        for team in self.teams:
            print(f"{team.sponsor}: {team.record}")
            
            
    def __ge__(self, other):
        # Allow comparison of tournaments based on the champion's total score
        if not isinstance(other, Tournament):
            return NotImplemented
        return self.champion.total_score >= other.champion.total_score


# Optimized subclass using dynamic programming to buy cars
class Tournament_optimised(Tournament):
    def __init__(self, config_path=None):
        super().__init__(config_path)
        
    def _purchase_inventory(self, team):
        #dynamic programming approach to optimize the purchase of cars
        sponsor_cars = [car for car in self.car_data if car["Make"] == team.sponsor]

        for car in sponsor_cars:
            car["Price"] = float(car["Price"])
            car["MPG-H"] = float(car["MPG-H"])
            
        n = len(sponsor_cars)
        W = int(team.budget)

        dp = [[0] * (W + 1) for _ in range(n + 1)]
        # Fill DP table
        for i in range(1,n+1):
            price = int(sponsor_cars[i-1]["Price"])
            mpg = int(sponsor_cars[i-1]["MPG-H"])
            for w in range(1,W+1):
                if w >= price:
                    dp[i][w] = max(dp[i-1][w], dp[i-1][w-price] + mpg)
                else:
                    dp[i][w] = dp[i-1][w]
        # Backtrack to find selected cars 
        selected = []
        w = W
        for i in range(n, 0, -1):  # backtrack from the last car
            if dp[i][w] != dp[i - 1][w]:
                car = sponsor_cars[i - 1]  # the i car is selected, i-1 because of 0-indexing
                selected.append(car)
                w -= int(car["Price"])  # update remaining budget

        # Update team inventory and budget
        new_cars = selected[::-1]
        team.inventory.extend(new_cars)  # load new cars into inventory
        team.total_car += len(new_cars)
        team.budget -= sum(car["Price"] for car in new_cars)