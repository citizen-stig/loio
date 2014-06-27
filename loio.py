#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lio - loseless image optimizator

import os
import sys
from PIL import Image
from base64 import standard_b64encode
import requests

TINYPNG_URL = "https://api.tinypng.com/shrink"
try:
    TINYPNG_API_KEY = os.environ['TINYPNG_API_KEY']
except KeyError:
    sys.stderr.write('Please set up TINYPNG_APY_KEY OS environment '
                     'variable and restart'
                     '\nYou can find it on https://tinypng.com/developers')
    exit(1)


def optimize_jpeg(input_filepath, output_filepath):
    """
    Reduce file size of JPG/JPEG image using PIL optimization
    """
    img = Image.open(input_filepath)
    img.save(output_filepath, optimize=True)


def optimize_png(input_filepath, output_filepath):
    """
    Reduce file size of PNG image using TinyPNG service
    """
    with open(input_filepath, 'rb') as f:
        raw_key = ("api:" + TINYPNG_API_KEY).encode('ascii')
        enc_key = standard_b64encode(raw_key).decode('ascii')
        resp = requests.post(TINYPNG_URL, data=f.read(), headers={
            "Authorization": "Basic %s" % enc_key
        })
        out_url = resp.headers['Location']

    with open(output_filepath, 'wb') as f:
        data = requests.get(out_url).content
        f.write(data)


def main():
    try:
        folder = sys.argv[1]
    except IndexError:
        sys.stderr.write('Please specify target folder')
        exit(1)
    user_input_msg = 'This script overwrites all images in specified folder. ' \
                     'Proceed?[yes/no]: '
    user_input = input(user_input_msg)
    while user_input.lower() not in ('yes', 'no'):
        user_input = input(user_input_msg)
    if user_input.lower() == 'no':
        exit(0)
    size_before = 0
    size_after = 0
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for file_name in filenames:
            sys.stdout.write('processing {0}...'.format(file_name))
            try:
                source_file_path = os.path.join(dirpath, file_name)

                img = Image.open(source_file_path)
                sys.stdout.write(img.format)

                size_before += os.stat(source_file_path).st_size

                optimize = globals()['optimize_' + img.format.lower()]
                try:
                    optimize(source_file_path, source_file_path)
                except Exception:
                    sys.stderr.write('\nSomething went wrong during '
                                     'optimization, skip\n')
                    continue
                finally:
                    size_after += os.stat(source_file_path).st_size
            except IOError:
                sys.stdout.write(' Not a image')
            except KeyError:
                sys.stdout.write(' Not supported for optimization')
            sys.stdout.write('\n')
    if size_before > 0:
        optimized_size = size_before - size_after
        optimized_percent = (optimized_size / size_before) * 100
        sys.stdout.write('Optimized {0} bytes, which is {1} '
                         'percent of size before'.format(optimized_size,
                                                         optimized_percent))


if __name__ == '__main__':
    main()
