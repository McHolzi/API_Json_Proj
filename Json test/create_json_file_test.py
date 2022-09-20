import json

x = [1,2,3,4,5]
param = {"param1" : 5, "param2" : "threshhold", "param3" : 6}
p = [4, 'hallo', 3.4, True, None]
p2 =['hi', 'ho', 'hu', 'ha', 'he']

dic = {}
for i in range(len(p)):
    dic[p2[i]] = p[i]
j = {
    "main": {
        "first": "hi",
        "second": x,
        "third": 1.5
    },
    "unimp": {
        "imp": param,
        "unimp2": dic
            }
}
with open('myfile.json','w') as outfile:
    json.dump(j, outfile, indent = 6)