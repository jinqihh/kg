import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="indir")
    parser.add_argument("-o", dest="outdir")
    args = parser.parse_args()
    indir = args.indir
    outdir = args.outdir
    file_out = open(os.path.join(outdir, "baikeTableRelation.txt"), "w")
    for file in os.listdir(indir):
        file_path = os.path.join(indir, file)
        file_in = open(file_path)
        for line in file_in.readlines():
            file_out.write(line)
        file_in.close()
    file_out.close()

