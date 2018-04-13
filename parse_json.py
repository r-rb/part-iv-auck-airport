import json


f = open('data.json','r',encoding="utf-8")

data = json.load(f)

ac_list = data["acList"]

interest = []
for entry in ac_list:
    try:
        if 'NZAA' in entry["To"]:
            interest.append(entry["Id"])
    except KeyError:
        pass

interest = list(set(interest))
print(len(interest))

print(*interest)
