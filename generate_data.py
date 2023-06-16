import pandas as pd
import numpy as np
import random
from urllib import parse
from sqlalchemy import create_engine
from datetime import timedelta, datetime
from unidecode import unidecode

games = pd.read_csv("data/games_to_choose.csv") 
male_names = pd.read_csv("data/male_names.csv")
female_names = pd.read_csv("data/female_names.csv")
male_surnames = pd.read_csv("data/male_surnames.csv")
female_surnames = pd.read_csv("data/female_surnames.csv")
addresses = pd.read_excel("data/addresses.xlsx", engine = "openpyxl")
games = games.rename(columns = {"Rent_price": "Rental_price"}).drop_duplicates("Game_ID")

def rand_email(name, surname):
    return (unidecode(random.choice([name, name[0]])) + "." + unidecode(surname) + random.choice(["", str(np.random.geometric(0.5))]) + random.choice(["@wp.pl", "@gmail.com", "@onet.pl"])).lower()

def rand_females(n):
    names = random.choices(female_names["IMIĘ PIERWSZE"], weights = female_names["LICZBA WYSTĄPIEŃ"], k = n)
    surnames = random.choices(female_surnames["Nazwisko aktualne"], weights = female_surnames["Liczba"], k = n)
    emails = [rand_email(name, surname) for name, surname in zip(names, surnames)]
    return [name + "*" + surname + "*" + email for name, surname, email in zip(names, surnames, emails)]

def rand_males(n):
    names = random.choices(male_names["IMIĘ PIERWSZE"], weights = male_names["LICZBA WYSTĄPIEŃ"], k = n)
    surnames = random.choices(male_surnames["Nazwisko aktualne"], weights = male_surnames["Liczba"], k = n)
    emails = [rand_email(name, surname) for name, surname in zip(names, surnames)]
    return [name + "*" + surname + "*" + email for name, surname, email in zip(names, surnames, emails)]

def rand_people(n):
    female_number = int(np.random.normal(0.5 * n, 0.02 * n))
    people = rand_females(female_number) + rand_males(n - female_number)
    random.shuffle(people)
    return people

def rand_phone_numbers(n):
    return ["+48" + random.choice(["5", "6", "7", "8"]) + str(random.randint(10**7, 10**8-1)) for I in range(n)]

def rand_dates_and_salaries(n, first_date):
    result = []
    for i in range(n):
        empl_date = first_date
        dism_date = None
        salary = None if dism_date else (5500 if datetime.now() - empl_date > timedelta(weeks = 26) else 4500)
        result.append((empl_date, dism_date, salary))
    return result

def rand_address():
    global addresses
    x = random.randint(0, len(addresses))
    address = addresses.loc[x, ["ULICA_NAZWA", "NUMER_ADR", "KOD_POCZTOWY"]]
    addresses = addresses.drop(x).reset_index(drop = True)
    return address[0][4:], address[1], "Wrocław", address[2]

def generate_customers(n, addresses_number):
    df = pd.DataFrame()
    df["Customer_ID"] = range(1, n+1)
    df[["First_name", "Last_name", "Email"]] = pd.Series(rand_people(n)).str.split("*", expand = True)
    df["Phone_number"] = rand_phone_numbers(n)
    df["Address_ID"] = [random.randint(1, addresses_number) for _ in range(n)]
    df = df.set_index("Customer_ID")
    return df

def generate_employees(n, addresses_number, first_date):
    df = pd.DataFrame()
    df["Employee_ID"] = range(1, n+1)
    df[["First_name", "Last_name", "Email"]] = pd.Series(rand_people(n)).str.split("*", expand = True)
    df["Phone_number"] = rand_phone_numbers(n)
    df["Address_ID"] = [random.randint(1, addresses_number) for _ in range(n)]
    df[["Employment_date", "Dismissal_date", "Salary"]] = rand_dates_and_salaries(n, first_date)
    df = df.set_index("Employee_ID")
    return df

def generate_addresses(n):
    df = pd.DataFrame()
    df["Address_ID"] = range(1, n+1)
    df[["Street", "Street_number", "City", "Postal_code"]] = [rand_address() for _ in range(n)]
    df = df.set_index("Address_ID")
    return df


def choose_games(games_to_choose, num_of_games):
    """
    Returns list with ID of games which the shop will be able to sale or rent.
    
    Arguments
    ---------
    games_to_choose_from_df - data frame with all games
    num_of_games - num of games' titles that the shop will be able to sale or rent
    """
    tournament_games = games_to_choose[games_to_choose["Tournament_game"] == 1]
    not_tournament_games = games_to_choose[games_to_choose["Tournament_game"] == 0]
    games_sample = not_tournament_games.sample(num_of_games - 5)
    not_tournament_id = list(games_sample["Game_ID"])
    tournament_id = list(tournament_games["Game_ID"])
    all_games = not_tournament_id + tournament_id
    game_df = games[games["Game_ID"].isin(all_games)].iloc[:, [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
    game_df["Game_ID"] = np.arange(1, len(game_df) + 1)
    game_df.set_index("Game_ID", inplace = True)
    all_games = list(game_df[game_df["Tournament_game"] == 0].index) + list(game_df[game_df["Tournament_game"] == 1].index)
    return all_games, game_df

def choose_products(games_to_choose_from, num_of_products, first_date):
    """
    Returns data frame with products that are available on the first day.
    
    Arguments
    ---------
    games_to_choose_from_df - data frame with all games that the shop will be able to sale or rent
    num_of_products - num of productst that the shop will stock on the first day
    """
    
    not_tournament_id = games_to_choose_from[-5:]
    tournament_products = [not_tournament_id[i] for i in np.arange(5)]*5
    for_rent_tournament = np.zeros(25)
    for_sale_tournament = np.zeros(25)
    for_tournament_tournament = [1 for i in np.arange(25)]
    
    not_tournament_products = random.choices(games_to_choose_from, k=num_of_products - 25)
    for_tournament_nt = [0 for i in np.arange(num_of_products - 25)]
    supply_date= [first_date for i in np.arange(num_of_products)]
    
    for_sale_nt = np.zeros(num_of_products - 25)
    for_rent_nt = np.zeros(num_of_products - 25)

    for i in np.arange(num_of_products - 25):
        rand = random.randint(0, 1)
        for_sale_nt[i] = rand
        if for_sale_nt[i] == 0:
            for_rent_nt[i] = 1
        else:
            for_rent_nt[i] = 0
            
    for_rent = list(for_rent_tournament) + list(for_rent_nt)
    for_sale = list(for_sale_tournament) + list(for_sale_nt)
    for_tournament = for_tournament_tournament + for_tournament_nt
    all_games_products = tournament_products + not_tournament_products
    
    product_df = pd.DataFrame()
    product_df["Product_ID"] = np.arange(1, num_of_products + 1)
    product_df["For_rent"] = for_rent
    product_df["For_sale"] = for_sale
    product_df["For_tournament"] = for_tournament
    product_df["Supply_date"] = supply_date
    product_df["Game_ID"] = all_games_products
    product_df["Purchase_ID"] = np.nan

    product_df["Supply_date"] = pd.to_datetime(product_df["Supply_date"])
    product_df["For_rent"] = pd.to_numeric(product_df["For_rent"], downcast='integer')
    product_df["For_sale"] = pd.to_numeric(product_df["For_sale"], downcast='integer')
    
    return product_df

def product_df_time(product_df, first_date): 
    
    cust_num = 501 #real customer number is cust_num - 1
    worker_num = 4 #real employee number is worker_num - 1
    
    rental_id = [0]
    rental_date = []
    return_date_expected = []
    return_date_actual = []
    customer_rent_id = []
    worker_rent_id = []
    
    relation_id = [0]
    product_id_rel = []
    rental_id_rel = []
    
    product_and_return = {}
    
    purchase_id = [0]
    purchase_date = []
    customer_purch_id = []
    worker_purch_id = []  
    
    tournament_id = [0]
    tournament_date = []
    ticket_price = []
    game_id = []
    tournament_cost = []
    
    tournament_id_score = []
    customer_id_score = []
    score = []
    
    num_to_rent = np.random.poisson(10, 365)
    num_to_sale = np.random.poisson(10, 365)
    
    num_to_supply = np.random.poisson(10, 365)
    
    j = 0
    for days_count in np.arange(1, 366):
        
        if days_count % 7 != 2:

            new_date = first_date + timedelta(days = int(days_count))

            games_rentable = product_df[product_df["For_rent"] == 1]

            num_of_games_to_rent = np.random.poisson(1/1.3, num_to_rent[j]) #ile gier na wypożyczenie?

            while sum(num_of_games_to_rent) > len(games_rentable): 
                num_of_games_to_rent = num_of_games_to_rent[:-1]

            random_return = np.random.random(len(num_of_games_to_rent))
            rent_cust_id = np.random.randint(1, cust_num, len(num_of_games_to_rent))
            rent_worker_id = np.random.randint(1, worker_num, len(num_of_games_to_rent))

            games_to_rent = games_rentable["Product_ID"].sample(sum(num_of_games_to_rent)) #jakie gry wypożyczono?

            k = 0
            i = 0
            for rent in num_of_games_to_rent:

                games_to_this_rent = np.array(games_to_rent)[k:k+rent]

                available_products = []

                for game in games_to_this_rent: #sprawdzamy, czy produkty są dostępne
                    if game not in list(product_and_return.keys()) or product_and_return[game] < new_date:
                        available_products.append(game)

                num_of_products = len(available_products)


                if num_of_products > 0:

                    rental_id.append(rental_id[-1]+1)
                    rental_date.append(new_date)
                    return_date_expected.append(new_date + timedelta(days = 3))
                    customer_rent_id.append(rent_cust_id[i])
                    worker_rent_id.append(rent_worker_id[i])

                    if random_return[i] < 0.5:
                        return_date_actual.append(return_date_expected[-1])
                        product_and_return[game] = return_date_expected[-1]

                    else:
                        return_date = new_date + timedelta(days = np.random.geometric(1/3))
                        return_date_actual.append(return_date)
                        product_and_return[game] = return_date

                    relation_id = relation_id + [relation_id[-1] + i for i in np.arange(1, num_of_products+1)]
                    rental_id_rel = rental_id_rel + [rental_id[-1]]*num_of_products
                    product_id_rel = product_id_rel + available_products

                k += rent
                i += 1


            #zakup gier

            games_salable = product_df[(product_df["For_sale"] == 1) & (pd.isna(product_df["Purchase_ID"]))]
            num_of_games_to_sale = np.random.geometric(1/1.3, num_to_sale[j]) #ile gier na wypożyczenie?
            purch_cust_id = np.random.randint(1, cust_num, len(num_of_games_to_sale))
            purch_worker_id = np.random.randint(1, worker_num, len(num_of_games_to_sale))
            random_cust = np.random.random(len(num_of_games_to_sale))

            while sum(num_of_games_to_sale) > len(games_salable): 
                num_of_games_to_sale = num_of_games_to_sale[:-1]

            games_to_sale = games_salable["Product_ID"].sample(sum(num_of_games_to_sale)) #jakie gry wypożyczono?

            k = 0
            i = 0

            for purchase in num_of_games_to_sale:

                games_to_this_purchase = np.array(games_to_sale)[k:k+purchase] 

                purchase_id.append(purchase_id[-1]+1)
                purchase_date.append(new_date)

                if random_cust[i] < 0.3:
                    customer_purch_id.append(purch_cust_id[i])
                else:
                    customer_purch_id.append(np.nan)

                worker_purch_id.append(purch_worker_id[i])

              
                for game_product in games_to_this_purchase:
                    product_df.loc[game_product, "Purchase_ID"] = purchase_id[-1]

                k += purchase
                i += 1

            games_to_supply = random.choices(all_games, k = num_to_supply[j])

            max_product_id = max(np.array(product_df["Product_ID"]))
            new_df = pd.DataFrame()
            new_df["Product_ID"] = np.arange(max_product_id + 1, max_product_id + num_to_supply[j] + 1)
            new_df["For_sale"] = [1 for _ in np.arange(num_to_supply[j])]
            new_df["For_rent"] = [0 for _ in np.arange(num_to_supply[j])]
            new_df["For_tournament"] = [0 for _ in np.arange(num_to_supply[j])]
            new_df["Supply_date"] = [new_date for _ in np.arange(num_to_supply[j])]
            new_df["Game_ID"] = games_to_supply
            new_df["Purchase_ID"] = np.nan

            new_df["Supply_date"] = pd.to_datetime(new_df["Supply_date"])
            new_df["For_rent"] = pd.to_numeric(new_df["For_rent"], downcast='integer')
            new_df["For_sale"] = pd.to_numeric(new_df["For_sale"], downcast='integer')

            product_df = pd.concat([product_df, new_df], ignore_index=True)  
            
            #turnieje gier
            
            if days_count % 7 == 1 or days_count % 7 == 0:
                if np.random.random() < 0.3:
                    tournament_id.append(tournament_id[-1] + 1)
                    tournament_date.append(new_date)
                    ticket_price.append(np.random.poisson(18))
                    game_id.append(np.random.choice(products_df[products_df["For_tournament"] == 1].loc[:, "Game_ID"].unique()))
                    tournament_cost.append(np.random.poisson(125))
                    
                    num_of_players = np.max([10, np.random.poisson(25)])
                    
                    while num_of_players >= cust_num - 1:
                        num_of_players =- 1
                        
                    if num_of_players > 0:
                        
                        customer_id_score = customer_id_score + list(np.random.choice(np.arange(cust_num), num_of_players, replace=False))
                        score = score + list(np.arange(num_of_players))
                        tournament_id_score = tournament_id_score + [tournament_id[-1] for _ in np.arange(num_of_players)]
                    

        j += 1
            
            

    score_id = np.arange(1, len(score) + 1)
    
    rental_df = pd.DataFrame({"Rental_ID":rental_id[1:], "Rental_date":rental_date, "Return_date_expected":return_date_expected, "Return_date_actual":return_date_actual, "Customer_ID":customer_rent_id, "Employee_ID":worker_rent_id}).set_index("Rental_ID")
    rental_product_rel_df = pd.DataFrame({"Relation_ID":relation_id[1:], "Product_ID":product_id_rel, "Rental_ID":rental_id_rel}).set_index("Relation_ID")
    purchase_df = pd.DataFrame({"Purchase_ID":purchase_id[1:], "Purchase_date":purchase_date, "Customer_ID":customer_purch_id, "Employee_ID":worker_purch_id}).set_index("Purchase_ID")
    tournament_df = pd.DataFrame({"Tournament_ID":tournament_id[1:], "Tournament_date":tournament_date, "Ticket_price":ticket_price, "Tournament_cost":tournament_cost, "Game_ID":game_id}).set_index("Tournament_ID")
    score_df = pd.DataFrame({"Score_ID":score_id, "Tournament_ID":tournament_id_score, "Customer_ID":customer_id_score, "Score":score}).set_index("Score_ID")
    product_df["Product_ID"] = range(1, len(product_df.index) + 1)
    product_df = product_df.dropna(subset = ["For_rent", "For_sale", "For_tournament"]).set_index("Product_ID")

    return rental_df, rental_product_rel_df, purchase_df, product_df, tournament_df, score_df


if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://{user}:{password}@{account}:3306/team03".format(
        user = "team03",
        password = parse.quote("te@m0e"),
        account = "giniewicz.it"
        )
    )

    conn = engine.connect()

    games_number = 50
    initial_products_number = 500
    customers_number = 500
    employees_number = 3
    first_date = pd.to_datetime("2022-04-29")
    address_df = generate_addresses(customers_number + employees_number)
    customer_df = generate_customers(customers_number, customers_number + employees_number)
    employee_df = generate_employees(employees_number, customers_number + employees_number, first_date)
    all_games, game_df = choose_games(games, games_number)
    products_df = choose_products(all_games, initial_products_number, first_date)
    rental_df, rental_product_rel_df, purchase_df, product_df, tournament_df, score_df = product_df_time(products_df, first_date)


    conn.execute("TRUNCATE TABLE customer")
    customer_df.to_sql("customer", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE employee")
    employee_df.to_sql("employee", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE address")
    address_df.to_sql("address", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE rental")
    rental_df.to_sql("rental", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE rental_product_rel")
    rental_product_rel_df.to_sql("rental_product_rel", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE product")
    product_df.to_sql("product", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE game")
    game_df.to_sql("game", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE tournament")
    tournament_df.to_sql("tournament", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE score")
    score_df.to_sql("score", engine, if_exists = "append")

    conn.execute("TRUNCATE TABLE purchase")
    purchase_df.to_sql("purchase", engine, if_exists = "append")

    conn.close()