
import json
import os 

# 直接爬取的json对象是key-dict形式，其中key是每个武器对象的名字
# 先将所有的key放入value中，形成一个大的dict对象，方便后面转换成csv文件
for file in os.listdir():
        suffix = file[-4:]
        if(suffix == 'json'):
                json_obj = None

                with open(file, 'r') as f:
                        json_obj = f.read()

                weapons = json.loads(json_obj)
                new_weapons = []
                for item in weapons:
                        name = [_ for _ in item.keys()][0]
                        value = item[name]
                        value['Name'] = name
                        new_weapons.append(value)

                with open(file, 'w') as f:
                        f.write(json.dumps(new_weapons))
