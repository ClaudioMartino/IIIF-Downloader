import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import iiif_downloader # import ../iiif_downloader.py

# URI template: {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}"
# begin = {scheme}://{server}{/prefix}/{identifier}

uri_begin = 'https://content.staatsbibliothek-berlin.de/dc/785884734-0001'
region_list = ['full', 'square', '125,15,120,140', 'pct:41.6,7.5,40,70']
size_list = ['full', 'max', '^max', '150,', '^360,', ',150', ',^240', 'pct:50', 'pct:120', '225,100', '^360,360', '!225,100', '^!360,360']
rotation_list = ['0', '22.5', '!0']
quality_list = ['color', 'gray', 'bitonal', 'default']
format_list = ['jpg', 'tif', 'png', 'gif', 'jp2', 'pdf', 'webp']

cnt = 1
for r in region_list:
    for s in size_list:
        for rot in rotation_list:
            for q in quality_list:
                for f in format_list:
                    uri = uri_begin + '/' + r + '/' + s + '/' + rot + '/' + q + '.' + f
                    print('[' + str(cnt) + '] ' + uri)
                    status = iiif_downloader.match_uri_pattern(uri)
                    if(status is None):
                        raise Exception
                    else:
                        if (status.group('begin') != uri_begin):
                            raise Exception
                        if (status.group('region') != r):
                            raise Exception
                        if (status.group('size') != s):
                            raise Exception
                        if (status.group('rotation') != rot):
                            raise Exception
                        if (status.group('quality') != q):
                            raise Exception
                        if (status.group('format') != f):
                            raise Exception
                    cnt = cnt + 1
