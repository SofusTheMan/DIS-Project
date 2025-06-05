import json
with open("data.json", "r") as f:
    data = json.load(f)


cleaned_data = []

for d in data:
    new_data = d.copy()
    del new_data["link"]
   
    new_data["GPA"] = new_data["GPA"].replace(",", ".")
    if not new_data["GPA"]:
        continue


    cleaned_data.append(new_data)
print(f'len(cleaned_data): {len(cleaned_data)}')


import csv
with open("scraped_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "GPA"])
    for d in cleaned_data:
        writer.writerow([d["title"], d["GPA"]])