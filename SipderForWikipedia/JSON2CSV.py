import csv
import json
import os 

class Convert:
    def getJsonObject(self, filename):
        with open(filename, 'r', 100, 'utf-8') as f:
            content = f.read()
            json_obj = json.loads(content)
            return json_obj

    def jsontocsv(self, filename):
        weapons = self.getJsonObject(filename)
        headers = set()

        for item in weapons:
            headers.update(set(item.keys()))
        
        headers = list(headers)
        with open(filename[:-4]+'csv', 'w', 100, 'utf-8') as f:
            fcsv = csv.DictWriter(f, headers)
            fcsv.writeheader()
            fcsv.writerows(weapons)

if __name__ == '__main__':
    sln = Convert()
   
    for file in os.listdir():
        suffix = file[-4:]
        if suffix == 'json':
            sln.jsontocsv(file)
