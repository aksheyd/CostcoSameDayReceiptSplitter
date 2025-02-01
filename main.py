# Parse HTML from Costco website and ask for who bought what and amounts
# Output a CSV file with the data

from bs4 import BeautifulSoup
import csv
import re

# Get the HTML from the Costco website
html_data = open("input.html", "r").read()
soup = BeautifulSoup(html_data, "html.parser")

all_text = soup.get_text()

num_items = re.findall(r"(\d+) Item", all_text)[0]
all_text = all_text.replace(f"{num_items} Item(s) in progress", "")


# Get the items
cleaned = all_text.split("Add instructions")

# Function to format the item details
def format_item_details(item_details):
    item_details = " ".join(item_details.split())
    match = re.search(r"(\d+)\s*Current price: \$(\d+\.\d+)", item_details)
    if match:
        quantity = match.group(1)
        price = match.group(2)
        item_details = re.sub(r"(\d+)\s*Current price: \$(\d+\.\d+)", f"Current price: ${price} ({quantity} items)", item_details)
    return item_details

def split_formatted_item(item):
    # print(item)
    match = re.search(r"^(.*?)(Current price: \$\d+\.\d+) (\(\d+ items\))", item)
    if match:
        name = match.group(1).strip()
        price = float(match.group(2).strip().replace("Current price: $", ""))
        count = int(match.group(3).strip().replace("(", "").replace(")", "").replace("items", ""))
        return (name, price, count)
    return (item, "", -1)

all_items = []
for i in cleaned:
    i = i.split("\n")
    formatted_item = []
    for j in i:
        if j.strip() != '':
            formatted_item.append(" ".join(j.split()))
    formatted_item = format_item_details(" ".join(formatted_item))
    split = split_formatted_item(formatted_item)
    all_items.append({
        "name": split[0],
        "price": split[1],
        "count": split[2]
        })
    
names = input("Enter the names of the people who bought the items separated by commas: ")
people = names.split(",")
price_per_person = {}
items_per_person = {}
for person in people:
    price_per_person[person] = 0
    items_per_person[person] = []

for i in range(0, len(all_items)):
    curr = all_items[i]
    print(f"Item {i+1}: {curr['name'], curr['price'], curr['count']}")

    j = 0
    while j < curr['count']:
        print("j", j)
        name = ""
        while any(n not in price_per_person for n in name.split(",") ):
            name = input(f"Who bought this? (You can split by entering names separated by commas): ")
            if any(n not in price_per_person for n in name.split(",")):
                print("Valid names are: ", price_per_person.keys())
    
        if "," in name:
            split_names = name.split(",")
            split_price = curr['price'] / float(curr['count']) / len(split_names)
            for split_name in split_names:
                split_name = split_name.strip()
                price_per_person[split_name] += split_price
                items_per_person[split_name].append(curr['name'])
            j += len(split_names) - 1
        else:
            price_per_person[name] += curr['price'] / float(curr['count'])
            items_per_person[name].append(curr['name'])
            j += 1

# Input tax and tip
tax = float(input("Enter the tax amount in dollars: "))
tip_percent = float(input("Enter the tip percentage: "))
tip = sum(price_per_person.values()) * (tip_percent / 100)

# Distribute tax and tip
total_additional = tax + tip
additional_per_person = total_additional / len(people)
for person in price_per_person:
    price_per_person[person] += additional_per_person

# Adjust to match actual total
actual_total = float(input("Enter the actual total amount: "))
calculated_total = sum(price_per_person.values())
adjustment = actual_total - calculated_total
adjustment_per_person = adjustment / len(people)
for person in price_per_person:
    price_per_person[person] += adjustment_per_person

# Output to CSV
with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Items Bought", "Total Price"])
    for person in price_per_person:
        writer.writerow([person, ", ".join(items_per_person[person]), round(price_per_person[person], 2)])
    writer.writerow(["Tax", "", round(tax, 2)])
    writer.writerow(["Tip", "", round(tip, 2)])
    writer.writerow(["Total", "", round(actual_total, 2)])
    writer.writerow(["Calculated Total", "", round(calculated_total, 2)])