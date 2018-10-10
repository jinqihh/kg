#this is the main script to scraw web pages

from mongo_queue import MongoQueue
from lxml import etree
import requests
import re
import multiprocessing
import random

re_numbers = re.compile(r"\n\[[0-9]+-?[0-9]*\]\n?")
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
headers2 = headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
headers = [headers1, headers2]
baike_queue = MongoQueue("scrawler", "baidubaike")

adapter = requests.adapters.HTTPAdapter(max_retries=20)

def start():
    if(baike_queue.db.count() == 0):
        baike_queue.push("https://baike.baidu.com/item/%E5%88%98%E5%BE%B7%E5%8D%8E/114923")
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
            head = headers[random.randint(0,1)]
            session.headers = head
            html = session.get(url).content
            html = html.decode("utf-8", "ignore")
            title, abstract, props, values, tongyi, tag, duoyi = parse(html)
            #props = "[SEP]".join(props)
            #values = "[SEP]".join(values)
            #print(type(title), type(abstract), type(props), type(values))
            baike_queue.complete(url, title, abstract, props, values, tongyi, tag, duoyi)
            #print('----------------------')
            
def parse(html):
    tree = etree.HTML(html)
    hrefs = tree.xpath("//a[contains(@href, '/item/')]")
    for ele in hrefs:
        target = ele.attrib["href"]
        if("http" in target or "force=1" in target):
            pass
        else:
            target = "https://baike.baidu.com" + target
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
            for ele in sub_ele.xpath(".//li/span"):
                duoyi.append(ele.text)
            for ele in sub_ele.xpath(".//li/a"):
                duoyi.append(ele.text)
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
    try:
        abstract = tree.xpath("//div[contains(@class, 'lemma-summary')]")[0]
        abstract = abstract.xpath("string(.)").strip()
        abstract = abstract.replace("\xa0", "")
        abstract = re.sub(re_numbers, "", abstract)
    except Exception as e:
        pass
    props = []
    values = []
    try:
        infobox = tree.xpath("//dl[contains(@class, 'basicInfo-block')]")
        for sub_infobox in infobox:
            prop = sub_infobox.xpath("./dt")
            for ele in prop:
                props.append(ele.text.replace("\xa0", ""))
            value = sub_infobox.xpath("./dd")
            for v in value:
                ret = v.xpath("string(.)").strip()
                ret = re.sub(re_shouqi, "", ret)
                values.append(ret)
    except Exception as e:
        pass
    return title, abstract, props, values, tongyi, tag, duoyi 


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
