import csv


# calcuate median values
def compute_median(numbers):
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n == 0:
        return None
    mid = n // 2
    if n % 2 == 1:
        return sorted_nums[mid]
    else:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
    
def process_csv(cardata_path):
    with open(cardata_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        car_data = list(reader)
    
    #cardata_path = "./data/cardata.csv"
    out_file_path = "./data/cardata_modified.csv"

    # 1. Data statistics for original (non-processed) data
    num_rows_original = len(car_data)
    num_columns_original = len(car_data[0]) if car_data else 0
    unique_make_count = len(set(row['Make'] for row in car_data))
    num_2009_entries = sum(1 for row in car_data if row['Year'] == '2009')
    
    # Calculate average MSRP for Impala and Integra models
    impala_prices = [float(row['MSRP']) for row in car_data if row['Model'] == 'Impala' and row['MSRP'].strip() != '']
    integra_prices = [float(row['MSRP']) for row in car_data if row['Model'] == 'Integra' and row['MSRP'].strip() != '']
    avg_impala_price = round(sum(impala_prices) / len(impala_prices), 2) if impala_prices else "0.00"
    avg_integra_price = round(sum(integra_prices) / len(integra_prices), 2) if integra_prices else "0.00"
    
    # Find the model with the fewest "Midsize" cars
    midsize_models = [row['Model'] for row in car_data if row['Vehicle Size'] == 'Midsize']
    if midsize_models:
        model_with_fewest_midsize = min(midsize_models, key=midsize_models.count)
    else:
        model_with_fewest_midsize = "N/A"
    
    # Return original data statistics as a list
    original_stats = [
        num_rows_original,
        num_columns_original,
        unique_make_count,
        num_2009_entries,
        avg_impala_price,
        avg_integra_price,
        model_with_fewest_midsize
    ]

    # define removed columns
    removed_columns = ['Engine Fuel Type', 'Market Category', 'Number of Doors', 'Vehicle Size']
        
    # remove corresponding columns
    for row in car_data:
        for col in removed_columns:
            row.pop(col)
            
    # use list comprehension to remove rows contain Ford, Kia, Lotus
    car_data = [row for row in car_data if row['Make'] not in ['Ford', 'Kia', 'Lotus']]

    # remove duplicate entries

    unique_data = []
    checked_data = set() #check duplicate value
    for row in car_data:
        row_tuple = tuple(sorted(row.items()))
        if row_tuple not in checked_data:
            checked_data.add(row_tuple)
            unique_data.append(row)

    #Column Header Renaming
    headermap = {
        "Make": "Make",
        "Model": "Model",
        "Year": "Year",
        "Engine HP": "HP",
        "Engine Cylinders": "Cylinders",
        "Transmission Type": "Transmission",
        "Driven_Wheels": "Drive",
        "Vehicle Style": "Style",
        "highway MPG": "MPG-H",
        "city mpg": "MPG-C",
        "Popularity": "Popularity",
        "MSRP": "Price"
    }

    for i, row in enumerate(unique_data):
        # Rename keys using the headermap, keep original if not in map
        unique_data[i] = {headermap.get(key, key): value for key, value in row.items()}
            
    # replace HP missing values with median value
        
    hp_values = [float(row["HP"]) for row in unique_data if row["HP"].strip() != '' ]
    median_hp = compute_median(hp_values)
    for row in unique_data:
        if row["HP"].strip() == '':
            row["HP"] = str(median_hp)
            

    # remove other missing values
    clean_data = []
    for row in unique_data:
        if all(value.strip() != '' for value in row.values()):
            clean_data.append(row)

    # create a new column HP_Type
    for row in clean_data:
        hp = float(row['HP'])
        if hp >= 300:
            row["HP_Type"] = 'high'
        else:
            row["HP_Type"] = 'low'
            
    # create a new column Price_class
    for row in clean_data:
        price = int(row["Price"])
        if price >= 50000:
            row["Price_class"] = 'high'
        elif 30000 <= price < 50000:
            row["Price_class"] = 'mid'
        else:
            row["Price_class"] = 'low'
            
    # round Price values nearest $100
    for row in clean_data:
        price = int(row["Price"])
        row["Price"] = str(round(price / 100) * 100)

    # Only cars made after Year 2000 will be retained
    clean_data = [row for row in clean_data if int(row["Year"]) > 2000]

    make_count = {}
    for row in clean_data:
        make = row["Make"]
        make_count[make] = make_count.get(make, 0) + 1

    valid_makes = {make for make, count in make_count.items() if 55 < count < 300}
    filtered_data =[]
    for row in clean_data:
        if row["Make"] in valid_makes:
            filtered_data.append(row)
            
    # Save to csv file
    with open(out_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=filtered_data[0].keys())
        writer.writeheader()
        writer.writerows(filtered_data)
        
    
    # Modified Data Statistics
    modified_data_stats = []
    modified_data_stats.append(len(filtered_data))  # Number of rows
    modified_data_stats.append(len(filtered_data[0]))  # Number of columns
    modified_data_stats.append(len(set(row['Make'] for row in filtered_data)))  # Number of unique 'Make'
    modified_data_stats.append(sum(1 for row in filtered_data if row['Year'] == '2009'))  # Number of entries from 2009

    # Average MSRP of "Impala" Model
    impala_prices = [float(row["Price"]) for row in filtered_data if row["Model"] == "Impala"]
    avg_price_impala = round(sum(impala_prices) / len(impala_prices), 2) if impala_prices else "N/A"
    
    modified_data_stats.append(avg_price_impala)
    
    # Average MSRP of "Integra" Model
    integra_prices = [float(row["Price"]) for row in filtered_data if row["Model"] == "Integra"]
    avg_price_integra = round(sum(integra_prices) / len(integra_prices), 2) if integra_prices else "N/A"
    
    modified_data_stats.append(avg_price_integra)
    
    # Model with the fewest "Midsize" cars
    midsize_count = {}
    for row in filtered_data:
        if row.get("Vehicle Size", '') == "Midsize":  # Check if the key exists
            model = row["Model"]
            midsize_count[model] = midsize_count.get(model, 0) + 1

    model_with_fewest_midsize = min(midsize_count, key=midsize_count.get, default="N/A")
    
    modified_data_stats.append(model_with_fewest_midsize)
    # Return modified data statistics as a list
    
    return original_stats, modified_data_stats
        



         

