#!/usr/bin/env python3
import argparse
import glob
import json
import os
import subprocess
import sys
import traceback
from argparse import ArgumentParser
from multiprocessing import Pool
from subprocess import Popen, PIPE, DEVNULL
from pathlib import Path
import m3u8
from urllib.parse import urlparse
import re

#import ipfshttpclient

parser = ArgumentParser(
    description=f"keep live"
)
subparsers = parser.add_subparsers(help="Command")
parser.set_defaults(command=lambda _: parser.print_help())


def download_with_curl(gateway,hash):

    # or api way
    url = f"https://{gateway}/api/v0/get?arg={hash}&archive=true" # &archive=true is more likey to bypass cache
    print('api ' + url)

    Path(f"./test/{gateway}").mkdir(parents=True, exist_ok=True)

    with open(f"./test/{gateway}/{hash}.log", "wb") as f:
        p = Popen(["curl", '-f', '-X','POST', url] , stdout=DEVNULL, stderr=f)
        p.wait() # wait for process to finish; this also sets the returncode variable inside 'res'
        #print(p.returncode)
        if p.returncode != 0:
            #print('chafa')
            raise Exception(f"{url} download failed, exit code {p.returncode}")
        else:
            print(f'finished downloading through {url}')


def download_with_curl_by_url(url):

    print('api ' + url)



    o = urlparse(url)

    folder = re.sub('[^A-Za-z0-9.]', '', o.netloc)
    path = re.sub('[^A-Za-z0-9.]', '', o.path)

    Path(f"./test/{folder}").mkdir(parents=True, exist_ok=True)

    with open(f"./test/{folder}/{path}.log", "wb") as f:
        p = Popen(["curl", '-f', url] , stdout=DEVNULL, stderr=f)
        p.wait() # wait for process to finish; this also sets the returncode variable inside 'res'
        #print(p.returncode)
        if p.returncode != 0:
            #print('chafa')
            raise Exception(f"{url} download failed, exit code {p.returncode}")
        else:
            print(f'finished downloading through {url}')

# def get_length(filename):
#     result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
#                              "format=duration", "-of",
#                              "default=noprint_wrappers=1:nokey=1", filename],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT)
#     return float(result.stdout)

def list_directory(gateway,cid):
    url = f"https://{gateway}/api/v0/ls?arg={cid}"
    p = Popen(["curl", '-s', '-f', '-X', 'POST', url], stdout=subprocess.PIPE, stderr=sys.stderr)
    result = p.communicate()[0] # wait for process to finish; this also sets the returncode variable inside 'res'
    # print(p.returncode)
    if p.returncode != 0:
        # print('chafa')
        raise Exception(f"{url} download failed, exit code {p.returncode}")
    else:
        return result.decode("utf-8")


cmd_test_gateway = subparsers.add_parser(
    "keep_alive",
    description="downloading folder through a gateway as tar archive",
    epilog="keep_alive"
)
cmd_test_gateway.add_argument(
    "cid", help="cid of folder")


cmd_test_gateway.add_argument(
    "-s",
    '--single-archive',
    help="download as single archive instead of individually (works with subdirectories)",
    action='store_true')

cmd_test_gateway.add_argument(
    "-g",
    '--gateway',
    help="gateway to use",
    default='ipfs.io') # the default one I use first, it uses 0.8.0

def run_test_gateway(args):
    """
    test downloading through gateways
    """
    if __name__ == '__main__':
        # gateways = [
        #     'ipfs.io',
        #     #'dweb.link',
        #     #'jacl.tech', # pinning also works :)
        # ]

        gateway = args.gateway

        # get a recursive list of file paths that matches pattern including sub directories
        file_list = glob.glob('./test/**/*.log', recursive=True)
        # Iterate over the list of filepaths & remove each file.
        for file_path in file_list:
            os.remove(file_path)

        if(args.single_archive):
            print('single archive')
            with Pool(5) as p:
                #arr = [(gateway, args.cid,) for gateway in gateways]
                #switch back to single one
                arr = [(gateway, args.cid,)]
                r = p.starmap_async(download_with_curl, arr)
                try:
                    r.get()
                except:
                    traceback.print_exc()
        else:
            print('download individually')
            with Pool(10) as p:
                gateways = [gateway]
                for gateway in gateways:
                    resp = list_directory(gateway,args.cid)
                    result = json.loads(resp)
                    links = result["Objects"][0]["Links"]
                    filtered_results = [link['Hash'] for link in links if link['Type'] == 2]

                    arr = [(gateway, result,) for result in filtered_results]
                    r = p.starmap_async(download_with_curl, arr )
                    try:
                        r.get()
                    except:
                        traceback.print_exc()

cmd_test_gateway.set_defaults(command=run_test_gateway)


cmd_m3u8 = subparsers.add_parser(
    "m3u8",
    description="generate m3u8 from ipfs directory",
    epilog="m3u8"
)
cmd_m3u8.add_argument(
    "cid", help="cid of folder")

cmd_m3u8.add_argument(
    "-g",
    '--gateway',
    help="gateway to use",
    default='ipfs.io') # the default one I use first, it uses 0.8.0

def gen_m3u8(args):
    """
    test downloading through gateways
    """
    if __name__ == '__main__':
        gateway = args.gateway
        resp = list_directory(gateway,args.cid)
        result = json.loads(resp)
        links = result["Objects"][0]["Links"]
        filtered_results = [(link['Hash'],link['Name']) for link in links if link['Type'] == 2]

        with open(f"./test/{args.cid}.m3u8", "w") as f:
            print('#EXTM3U',file=f)
            for pair in filtered_results:
                path=pair[1]
                filename, file_extension = os.path.splitext(path)
                if file_extension.lower() not in ['.mp3','.m4a']:
                    continue
                print(f'#EXTINF:-1,{filename}', file=f)
                print(f'https://{gateway}/ipfs/{pair[0]}', file=f)

cmd_m3u8.set_defaults(command=gen_m3u8)

cmd_test_playlist = subparsers.add_parser(
    "test_playlist",
    description="downloading playlist through gateway",
    epilog="test_playlist"
)
cmd_test_playlist.add_argument(
    "playlist", help="m3u playlist")


def run_test_playlist(args):
    """
    test downloading through gateways
    """
    if __name__ == '__main__':

        # get a recursive list of file paths that matches pattern including sub directories
        file_list = glob.glob('./test/**/*.log', recursive=True)
        # Iterate over the list of filepaths & remove each file.
        for file_path in file_list:
            os.remove(file_path)

        playlist = m3u8.load(args.playlist)
        files = playlist.files

        print('download individually')
        with Pool(10) as p:
            arr = [(file,) for file in files]
            r = p.starmap_async(download_with_curl_by_url, arr)
            try:
                r.get()
            except:
                traceback.print_exc()

cmd_test_playlist.set_defaults(command=run_test_playlist)


# Finally, use the new parser
all_args = parser.parse_args()
# Invoke whichever command is appropriate for the arguments
all_args.command(all_args)
