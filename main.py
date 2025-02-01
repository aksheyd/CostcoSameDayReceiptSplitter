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

    for j in range(0, curr['count']):
        name = ""
        while name not in price_per_person:
            name = input(f"Who bought this?")
            if name not in price_per_person:
                print("valid names are: ", price_per_person.keys())

        price_per_person[name] += curr['price'] / float(curr['count']) 
        items_per_person[name].append(curr['name'])
    
# print(price_per_person)
with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Items Bought", "Total Price"])
    for person in price_per_person:
        writer.writerow([person, ", ".join(items_per_person[person]), price_per_person[person]])