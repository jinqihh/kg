from pymongo import MongoClient
import re
re_deng = re.compile(r"等$")
re_num = re.compile(r"、\[[0-9]+\]")
re_han = re.compile(r"[\u4e00-\u9fa5]")

def process(value):
    ret = []
    value = value.strip()
    value = re.sub(re_deng, "", value)
    value = re.sub(re_num, "", value)
    if("，" not in value):
        if(";" in value):
            ret = value.split(";")
        elif("、" in value):
            ret = value.split("、")
        #elif("," in value):
        #    ret = value.split(",")
        #elif(re.search(re_han, value)):
        #   ret = value.split(" ")
        else:
            ret = [value]
        return ret
    else:
        size = len(value)
        found = False
        temp = ""
        for i in range(size):
            if(value[i] == '（'):
                found = True
            elif(value[i] == '）'):
                found = False
            elif(value[i] == '，'):
                if(found == False):
                    ret.append(temp)
                    temp = ""
                else:
                    temp += value[i]

        ret_2 = []
        for ele in ret:
            ret_2.extend(ele.split("、"))
        return ret_2






if __name__ == "__main__":
    client = MongoClient()
    Client = client["scrawler"]
    db = Client["baidubaike"]
    fout = open("infobox_triplets.txt", "w")
    inserted = db.find({"status":3})
    for item in  inserted:
        #url = item["_id"]
        title = item["title"]
        #abstract = item["abstract"]
        #duoyi = item["duoyi"]
        props = item["props"]
        values = item["values"]
        #tongyi = item["tongyi"]
        tag = item["tag"]
        for prop, value in zip(props, values):
            ret = []
            ret = process(value)
            for sub_ele in ret:
                sub_ele = sub_ele.strip()
                if(sub_ele != ""):
                    fout.write("%s\t%s\t%s\n" %  (title, prop, sub_ele))
    fout.close()


