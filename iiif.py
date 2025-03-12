import json
import os
from shutil import rmtree
from urllib.request import urlopen, Request

# TODO: download one specific page
# TODO: read manifest from url (don't download)

def open_url(u):
  headers = {'User-Agent' : "Mozilla/5.0"}
  try:
    response = urlopen(Request(u, headers = headers), timeout = 30)
    #print(response.getcode())
    page = response.read()
    return page
  except Exception as err:
    print(Exception, err)
    return;

def download_file(u, filepath):
  with open(filepath, 'xb') as file:
    try:
      file.write(open_url(u))
      return True
    except Exception as err:
      print(Exception, err)
      os.remove(filepath)
      return False

def find_keys(data, key):
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                yield v
            yield from find_keys(v, key)
    elif isinstance(data, list):
        for item in data:
            yield from find_keys(item, key)

def get_extension(mime_type):
    mime_to_extension = {
        'image/jpeg': '.jpg',
        'image/tiff': '.tif',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/jp2': '.jp2',
        'application/pdf': '.pdf',
        'image/webp': '.webp'
    }
    return mime_to_extension.get(mime_type, None)

def get_img_url(iiif_id, ext):
    region = 'full'
    size = 'max' # or 'full'
    rotation = '0'
    quality = 'default'
    img_url = iiif_id + '/' + region + '/' + size + '/' + rotation + '/' + quality + ext
    return img_url

def read_iiif_json(d):
    # Read label and use it as new directory title
    title = d['label']

    # Find canvases and resources in json
    canvases = list(find_keys(d["sequences"], 'canvases'))
    resources = list(find_keys(canvases[0], 'resource'))
    
    # Titles of the files in canvases (it is usually a number)
    labels = []
    for c in canvases[0]:
        if 'label' in c:
            labels.append(c['label'])

    # Look for file features in resources
    iiif_ids = []
    iiif_formats = []
    iiif_w = []
    iiif_h = []
    for r in resources:
        if '@id' in r:
            iiif_ids.append(r['@id'])
        if 'format' in r:
            iiif_formats.append(r['format'])
        if 'width' in r:
            iiif_w.append(r['width'])
        if 'height' in r:
            iiif_h.append(r['height'])

    if(len(labels) != len(iiif_ids) != len(iiif_formats) != len(iiif_w) != len(iiif_h)):
        raise Exception("len discrepancy") 

    return title, labels, iiif_ids, iiif_formats, iiif_w, iiif_h

def download_iiif_files(iiif_ids, labels, iiif_formats, iiif_w, iiif_h, subdir):
    some_error = False
    for cnt, iiif_id in enumerate(iiif_ids):
        print('[' + str(cnt + 1) + '/' + str(len(iiif_ids)) + '] Label: ' + labels[cnt])
        print('- ID: ' + iiif_id)
        ext = get_extension(iiif_formats[cnt])
        print('- Format: ' + iiif_formats[cnt] + ' => Extension: ' + ext)
        print('- Width: ' + str(iiif_w[cnt]) + 'px')
        print('- Height: ' + str(iiif_h[cnt]) + 'px')
        img_url = get_img_url(iiif_id, ext)
        print('- URL: ' + img_url)
        filename = 'p' + str(cnt + 1).zfill(3) + ext
        if(download_file(img_url, subdir + '/' + filename)):
            print('\033[92m' + '- ' + filename + ' saved in ' + subdir + '.' + '\033[0m')
        else:
            print('\033[91m' + '- Error!' + '\033[0m')
            some_error = True
    return some_error

def download_iiif_files_from_manifest(manifest_name, maindir):
    # Doc: https://iiif.io/api/image/3.0/
    with open(manifest_name) as f:
        d = json.load(f)

    # Read manifest
    title, labels, iiif_ids, iiif_formats, iiif_w, iiif_h = read_iiif_json(d)
    print('- Title: ' + title)
    print('- Files: ' + str(len(labels)))

    # Create subdirectory from title
    title = title.replace("/", " ")
    title = title.replace(":", "")
    subdir = maindir + '/' + title
    if os.path.exists(subdir):
        rmtree(subdir)
    os.mkdir(subdir)

    # Download images from url
    some_error = download_iiif_files(iiif_ids, labels, iiif_formats, iiif_w, iiif_h, subdir)

    # Rename directory if something was wrong
    if(some_error):
        err_subdir = maindir + '/' + 'ERR_' + title
        if os.path.exists(err_subdir):
            rmtree(err_subdir)
        os.rename(subdir, err_subdir)
        print('\033[91m' + 'Some error with ' + title + '.\033[0m') 
