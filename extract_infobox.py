from pymongo import MongoClient
import re
re_deng = re.compile(r"等$|等、个$")
re_num = re.compile(r"、\[[0-9]+\]")
re_han_book = re.compile(r"^(《[\u4e00-\u9fa5a-zA-Z·：]+》(\s*|、))*《[\u4e00-\u9fa5·：a-zA-Z]+》$")
re_han2 = re.compile(r"^([\u4e00-\u9fa5·]+(\s)+)+[\u4e00-\u9fa5·]+$")
shuxian = ["定义域", "值域", "符号", "偏旁", "笔顺顺序", "运用"]



def preprocess_value(value):
    value = value.strip()
    value = value.replace("\xa0", " ")
    value = value.replace("\u200e", "")
    value = value.replace("\u3000", " ")
    value = value.replace("\u200d", "")
    value = re.sub(re_num, "", value)
    value = re.sub(re_deng, "", value)
    return value
def cut_value(value, prop):
    ret = []
    #处理 | 分割的情况
    if("|" in value and prop not in shuxian):
        ret = value.split("|")
        return ret
    #处理《》分割的情况，同时去掉书名号
    elif(re.match(re_han_book, value)):
        temp = ""
        for i in range(len(value)):
            if(value[i] == "》"):
                ret.append(temp)
                temp = ""
            elif(value[i] == "《"):
                pass
            else:
                temp += value[i]
        return ret
    #处理 由空格分割的多个汉字词语的情况, 增加了判断是否分割之后所有的词语都是单字的情况

    elif(re.match(re_han2, value)):
        temp = value.split()
        danshu = True
        for i in temp:
            if(len(i) > 1):
                danshu = False
                break
        if(danshu):
            return [value]
        else:
            return temp
    elif("，" not in value):
        number_in = re.search("[0-9]", value)
        http_in = "http" in value
        kuohao_in = "（" in value or "(" in value
        size = len(value)
        if("；" in value):
            ret = value.split("；")
        elif(";" in value):
            ret = value.split(";")
        elif("," in value and not number_in and not kuohao_in):
            ret = value.split(",")
        elif("、" in value):
            found = False
            temp = ""
            for i in range(size):
                if(value[i] == '（'):
                    found = True
                    temp += value[i]
                elif(value[i] == '）'):
                    found = False
                    temp += value[i]
                elif(value[i] == '、'):
                    if(found == False):
                        ret.append(temp)
                        temp = ""
                    else:
                        temp += value[i]
                else:
                    temp += value[i]
            if(temp != ""):
                ret.append(temp)
            ret_2 = []
            for i in ret:
                if(re.match(re_han2, i)):
                    ret_2.extend(i.split())
                else:
                    ret_2.append(i)
            ret = ret_2
        elif("\\" in value):
            if(number_in or http_in or kuohao_in):
                ret = [value]
            elif("男" in value):
                ret = [value]
            else:
                temp = value.split("\\")
                for item in temp:
                    if("/" in item):
                        ret.extend(item.split("/"))
                    else:
                        ret.append(item)
        elif("/" in value):
            if(number_in or http_in or kuohao_in):
                ret = [value]
            else:
                ret = value.split("/")
        #elif("," in value):
        #    ret = value.split(",")
        #elif(re.search(re_han, value)):
        #   ret = value.split(" ")
        else:
            ret = [value]
        return ret
    else:
        #print("hhh")
        size = len(value)
        found = False
        temp = ""
        for i in range(size):
            if(value[i] == '（'):
                found = True
                temp += value[i]
            elif(value[i] == '）'):
                found = False
                temp += value[i]
            elif(value[i] == '，'):
                if(found == False):
                    ret.append(temp)
                    temp = ""
                else:
                    temp += value[i]
            else:
                temp += value[i]
        if(temp != ""):
            ret.append(temp)
        #print(ret)

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
    for i, item in  enumerate(inserted, 1):
        #url = item["_id"]
        print(i)
        title = item["title"]
        #abstract = item["abstract"]
        #duoyi = item["duoyi"]
        props = item["props"]
        values = item["values"]
        #tongyi = item["tongyi"]
        tag = item["tag"]
        for prop, value in zip(props, values):
            ret = []
            value = preprocess_value(value)
            ret = cut_value(value, prop)
            for sub_ele in ret:
                sub_ele = sub_ele.strip()
                if(sub_ele != ""):
                    fout.write("%s\t%s\t%s\n" %  (title, prop, sub_ele))
    fout.close()


