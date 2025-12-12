from tournament import Tournament, Tournament_optimised

# sponsor = ["FIAT", "Audi", "Chrysler", "Mitsubishi", "Ferrari",
#             "Saab", "Porsche", "Hyundai", "Oldsmobile",
#             "Mercedes-Benz", "Lincoln", "Subaru", "Buick", "Lexus", "Pontiac", "Acura"]
sponsor = ["Mercedes-Benz", "Lincoln", "Chrysler", "Buick", "Bentley",
            "Saab", "Porsche", "Hyundai", "Land Rover", "Ferrari", "Subaru", "Aston Martin", "Volvo", "Oldsmobile", "Scion", "Lexus"]
t3 = Tournament("./data/config.json")
t3.generate_sponsors(sponsor_list=sponsor,fixed_budget=500000)
t3.generate_teams()
t3.buy_cars()
t3.hold_event()

t4 = Tournament_optimised("./data/config.json")
t4.generate_sponsors(sponsor_list=sponsor,fixed_budget=500000)
t4.generate_teams()
t4.buy_cars()
t4.hold_event()