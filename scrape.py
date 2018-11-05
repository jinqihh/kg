#this is the main script to scraw web pages

from mongo_queue import MongoQueue
from lxml import etree
import requests
import re
import multiprocessing
import random
from urllib import parse

re_numbers = re.compile(r"\n\[[0-9]+-?[0-9]*\]\xa0\n")
re_shouqi = re.compile(r"展开.*收起", re.DOTALL)
headers1 = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }
agents = [
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
    "Mozilla/2.02E (Win95; U)",
    "Mozilla/3.01Gold (Win95; I)",
    "Mozilla/4.8 [en] (Windows NT 5.1; U)",
    "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
    "HTC_Dream Mozilla/5.0 (Linux; U; Android 1.5; en-ca; Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.2; U; de-DE) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/234.40.1 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; sdk Build/CUPCAKE) AppleWebkit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; htc_bahamas Build/CRB17) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1-update1; de-de; HTC Desire 1.19.161.5 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Sprint APA9292KT Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-ch; HTC Hero Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; ADR6300 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; HTC Legend Build/cupcake) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic Build/PLAT-RC33) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1 FirePHP/0.3",
    "Mozilla/5.0 (Linux; U; Android 1.6; en-us; HTC_TATTOO_A3288 Build/DRC79) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.0; en-us; dream) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; T-Mobile G1 Build/CRB43) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari 525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-gb; T-Mobile_G2_Touch Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Droid Build/ESD20) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Droid Build/FRG22D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Milestone Build/ SHOLS_U2_01.03.1) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.0.1; de-de; Milestone Build/SHOLS_U2_01.14.0) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522  (KHTML, like Gecko) Safari/419.3",
    "Mozilla/5.0 (Linux; U; Android 1.1; en-gb; dream) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Droid Build/ESD20) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Sprint APA9292KT Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; ADR6300 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-ca; GT-P1000M Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 3.0.1; fr-fr; A500 Build/HRI66) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 1.6; es-es; SonyEricssonX10i Build/R1FA016) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.6; en-us; SonyEricssonX10i Build/R1AA056) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
]
headers2 = headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
headers = [headers1, headers2]
baike_queue = MongoQueue("scrawler", "baidubaike2")
start_url = ["https://baike.baidu.com/item/%E5%88%98%E5%BE%B7%E5%8D%8E/114923",
        "https://baike.baidu.com/item/%E4%B8%AD%E5%9B%BD/1122445",
        "https://baike.baidu.com/item/%E9%98%BF%E5%B0%94%E4%BC%AF%E7%89%B9%C2%B7%E7%88%B1%E5%9B%A0%E6%96%AF%E5%9D%A6/127535",
        "https://baike.baidu.com/item/%E6%95%B0%E5%AD%A6/107037?fr=aladdin",
        "https://baike.baidu.com/item/%E4%BD%93%E8%82%B2",
        "https://baike.baidu.com/item/%E7%BE%8E%E9%A3%9F",
        "https://baike.baidu.com/item/%E5%8C%BB%E5%AD%A6",
        "https://baike.baidu.com/item/%E7%A7%91%E5%AD%A6%E6%8A%80%E6%9C%AF",
        "https://baike.baidu.com/item/%E8%8B%B9%E6%9E%9C/5670"
        ]

adapter = requests.adapters.HTTPAdapter(max_retries=20)
re_direct = re.compile("https://baike.baidu.com/item/(.+)/([0-9]+)\?fromtitle=(.+)&fromid=([0-9]+)")
def redirect(url):
    try:
        ret = re.match(re_direct, url)
        return (ret.group(1), ret.group(2), ret.group(3), ret.group(4))
    except Exception:
        return ("", "", "", "")
def start():
    if baike_queue.db.count() == 0:
        for url in start_url:
            url = parse.unquote(url, "utf-8")
            baike_queue.push(url)
    #if(baike_queue.db.count() == 0):
    #    baike_queue.push("https://baike.baidu.com/item/%E5%88%98%E5%BE%B7%E5%8D%8E/114923")
    session = requests.Session()
    session.mount("https://", adapter)
    while(True):
        try:
            url = baike_queue.pop()
            print("正在处理 ", url)
        except KeyError:
            print("队列没有数据")
            break
        else:
            head = agents[random.randint(0,61)]
            session.headers = head
            response = session.get(url)
            cur_url = parse.unqoute(response.url, "utf-8")
            html = response.content.decode("utf-8", "ignore")
            title, abstract, props, values, tongyi, tag, duoyi, abstract_list, infobox_list, hrefs_list = parse(html)
            redirect = ""
            if(url != cur_url):
                cur_title, cur_id, from_title, from_id = redirect(cur_url)
                if(cur_title != "" && cur_id != "" && from_title != ""):
                    title = from_title
                    redirect = "https://baike.baidu.com/" + cur_title + "/" + cur_id
            #props = "[SEP]".join(props)
            #values = "[SEP]".join(values)
            #print(type(title), type(abstract), type(props), type(values))
            baike_queue.complete(url, title, abstract, props, values, tongyi, tag, duoyi, abstract_list, infobox_list, hrefs_list, redirect)
            #print('----------------------')
            
def parse(html):
    tree = etree.HTML(html)
    hrefs = tree.xpath("//a[contains(@href, '/item/')]")
    href_dict = dict()
    for ele in hrefs:
        target = ele.attrib["href"]
        old_href = target
        if("http" in target or "force=1" in target):
            pass
        else:
            target = "https://baike.baidu.com" + target
            target = parse.unquote(target, "utf-8")
            target = target.strip("#ViewPageContent")
            if("fromtitle" in target):
                cur_title, cur_id, from_title, from_id = redirect(target)
                target = "https://baike.baidu.com/" + from_title + "/" + from_id
            if(old_href not in href_dict):
                href_dict[old_href] = (target, 1)
            else:
                href_dict[old_href][1] += 1
            href_dict[old_href] = target
            baike_queue.push(target)
    #get page title, abtract, infobox
    title = ""
    try:
        title = tree.xpath("//dd[contains(@class, 'lemmaWgt-lemmaTitle-title')]")
        title = title[0].xpath("./h1")[0].text
    except Exception as e:
        pass
    tongyi = ""
    try:
        tongyi_ele = tree.xpath("//span[contains(@class, 'view-tip-panel')]")[0]
        tongyi = tongyi_ele.xpath("string(.)").strip()
    except Exception as e:
        pass
    duoyi = []
    try:
        duoyi_ele = tree.xpath("//ul[contains(@class, 'polysemantList-wrapper')]")
        for sub_ele in duoyi_ele:
            for ele in sub_ele.xpath(".//li/a"):
                temp = ele.attrib["href"]
                duoyi.append(href_dict[temp][0])

    except Exception as e:
        pass
    tag = []
    try:
        tag_ele = tree.xpath("//span[contains(@class, 'taglist')]")
        for ele in tag_ele:
            temp = ele.xpath("./a")
            if(temp != []):
                tag.append(temp[0].text)
            else:tag.append(ele.text.strip("\n"))
    except Exception:
        pass
    abstract = ""
    abstract_dict = dict()
    try:
        abstract_ele = tree.xpath("//div[contains(@class, 'lemma-summary')]")[0]
        abstract = abstract_ele.xpath("string(.)").strip()
        abstract = abstract.replace("\xa0", "")
        abstract = re.sub(re_numbers, "", abstract)
        abstract_hrefs = abstract_ele.xpath(".//a")
        for ele in abstract_hrefs:
            href = ele.attrib["href"]
            entity = ele.text
            true_href = href_dict[href][0]
            if(true_href not in abstract_dict):
                abstract_dict[true_href] = (entity, 1)
            else:
                abstract_dict[true_href][1] += 1
    except Exception as e:
        pass
    infoTriples = dict()
    infobox_dict = dict()
    try:
        infobox = tree.xpath("//dl[contains(@class, 'basicInfo-block')]")
        for sub_infobox in infobox:
            if "overlap" not in sub_infobox.attrib["class"]:
                prop_eles = sub_infobox.xpath("./dt")
                value_eles = sub_infobox.xpath("./dd")
                for prop_ele, value_ele in zip(prop_eles, value_eles):
                    prop_text = prop_ele.xpath("string(.)").strip().replace("\xa0", "")
                    value_text = value_ele.xpath("string(.)").strip()
                    value_text = re.sub(re_numbers, "", value_text)
                    value_text = re.sub("\n+", "、", value_text)
                    infoTriples[prop_text] = value_text
            else:
                prop_eles = sub_infobox.xpath("./dt")
                value_eles = sub_infobox.xpath(".//dd")
                for prop_ele, value_ele in zip(prop_eles, value_eles):
                    prop_text = prop_ele.xpath("string(.)").strip().replace("\xa0", "")
                    value_text = value_ele.xpath("string(.)").strip()
                    value_text = re.sub(re_numbers, "", value_text)
                    value_text = value_text.strip("收起")
                    value_text = re.sub("\n+", "、", value_text)
                    infoTriples[prop_text] = value_text
        infobox_hrefs = infobox.xpath(".//a")
        for ele in infobox_hrefs:
            temp = ele.attrib["href"]
            entity = ele.text
            true_href = href_dict[temp][0]
            if(true_href not in infobox_dict):
                infobox_dict[true_href] = (entity, 1)
            else:
                infobox_dict[true_href][1] += 1
    except Exception as e:
        pass
    props = []
    values = []
    for key, value in infoTriples.items():
        props.append(key)
        values.append(value)
    abstract_list = []
    for key, value in abstract_dict.items():
        abstract_list.append((key, value[0], value[1]))
    infobox_list = []
    for key, value in abstract_dict.item():
        infobox_list.append((key, value[0], value[1]))
    hrefs_list = href_dict.values()
    return title, abstract, props, values, tongyi, tag, duoyi, abstract_list, infobox_list, hrefs_list 


def process_crawler():
    process = []
    num_cpus = multiprocessing.cpu_count()
    print("将启动进程数为 ", num_cpus)
    for i in range(num_cpus):
        p = multiprocessing.Process(target=start)
        p.start()
        process.append(p)
    for p in process:
        p.join()

    


if __name__ == "__main__":

    #start("https://baike.baidu.com/item/%E5%88%98%E5%BE%B7%E5%8D%8E/114923")
    process_crawler()
