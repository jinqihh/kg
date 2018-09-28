import os
import argparse
import re

src_pattern = re.compile(r"<img src=\"(.*)\" class=\"authorityIcon\" title=\".*\"/>")
url = "url:"
def preprocess(line, pre, fout):
    line = line.strip()
    pre_sub = pre[0]
    img = re.search(src_pattern, line)
    found = False
    if(img):
        img_url = img.group(1)
        line = re.sub(src_pattern, "", line)
        found = True
    sub, predict, obj = line.split(maxsplit=2)
    if(found and pre_sub != sub):
        fout.write("%s\t%s\t%s\n" % (sub, url, img_url))
    if("，" in obj):
        if("、" not in obj):
            for i in obj.split("，"):
                fout.write("%s\t%s\t%s\n" % (sub, predict, i))
        else:
            for i in obj.split("，"):
                for item in i.split("、"):
                    fout.write("%s\t%s\t%s\n" % (sub, predict, item))
    elif("、" in obj):
        for i in obj.split("、"):
            fout.write("%s\t%s\t%s\n" % (sub, predict, i))
    else:
        fout.write("%s\t%s\t%s\n" % (sub, predict, obj))
    pre[0] = sub


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="indir")
    parser.add_argument("-o", dest="outdir")
    args = parser.parse_args()
    indir = args.indir
    outdir = args.outdir

    for file in os.listdir(indir):
        file_path = os.path.join(indir, file)
        fin = open(file_path)
        fileout_path = os.path.join(outdir, file)
        fout = open(fileout_path, "w")
        pre = [None]
        for i, line in enumerate(fin.readlines(), 1):
            preprocess(line, pre, fout)
            print(pre[0])
        fin.close()
        fout.close()

