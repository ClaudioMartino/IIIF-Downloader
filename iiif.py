import json
import os
from shutil import rmtree
from urllib.request import urlopen, Request

# Doc: https://iiif.io/api/image/2.0/

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

def is_url(url):
    return (url[:4] == 'http')

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
    if(iiif_id.endswith(ext)):
        img_url = iiif_id
    else:
        region = 'full'
        size = 'max' # or 'full'
        rotation = '0'
        quality = 'default'
        img_url = iiif_id + '/' + region + '/' + size + '/' + rotation + '/' + quality + ext
    return img_url

def read_iiif2_json(d):
    title = d['label']

    sequences = d["sequences"]
    # Assumption: 1 sequence in sequences
    sequence = sequences[0]
    canvanses = sequence.get("canvases")

    labels = []
    images = []
    for c in canvanses:
        labels.append(c.get("label"))
        # Assumption: 1 image in images
        images.append(c.get("images")[0])

    resources = []
    for i in images:
        resources.append(i.get("resource"))

    iiif_ids = []
    iiif_formats = []
    iiif_w = []
    iiif_h = []
    for r in resources:
        iiif_ids.append(r.get('@id'))
        iiif_formats.append(r.get('format'))
        iiif_w.append(r.get('width'))
        iiif_h.append(r.get('height'))

    if(len(labels) != len(iiif_ids) != len(iiif_formats) != len(iiif_w) != len(iiif_h)):
        raise Exception("len discrepancy") 

    return title, labels, iiif_ids, iiif_formats, iiif_w, iiif_h

def read_iiif_json(d):
    # Check
    context = d['@context']
    if(context.endswith('2/context.json')):
        return read_iiif2_json(d)
    else:
        # TODO Other standars
        raise Exception("Only IIIF 2.0 is supported today") 

def sanitize_name(title):
    title = title.replace("/", " ")
    title = title.replace(":", "")
    return title

def download_iiif_files(iiif_ids, labels, iiif_formats, iiif_w, iiif_h, subdir, firstpage = 1, lastpage = -1, use_page_number = False):
    # Create sub-array
    totpages = len(iiif_ids)
    if(firstpage != 1 or lastpage != -1):
        iiif_ids = iiif_ids[firstpage-1:]
        iiif_ids = iiif_ids[:lastpage-firstpage+1]
        print("- Downloading pages " + str(firstpage) + "-" + str(lastpage) + " from a total of " + str(totpages))

    # Loop over each id
    some_error = False
    for cnt, iiif_id in enumerate(iiif_ids):
        percentage = round((cnt + 1) / len(iiif_ids) * 100, 1)
        cnt = cnt + firstpage - 1
        print('[p.' + str(cnt + 1) + '/' + str(totpages) + '; '  + str(percentage) + '%] Label: ' + labels[cnt])
        print('- ID: ' + iiif_id)
        ext = get_extension(iiif_formats[cnt])
        print('- Format: ' + iiif_formats[cnt] + ' => Extension: ' + ext)
        print('- Width: ' + str(iiif_w[cnt]) + 'px')
        print('- Height: ' + str(iiif_h[cnt]) + 'px')
        img_url = get_img_url(iiif_id, ext)
        print('- URL: ' + img_url)
        if(use_page_number):
            filename = 'p' + str(cnt + 1).zfill(3) + ext
        else:
            filename = sanitize_name(labels[cnt]) + ext
        if(download_file(img_url, subdir + '/' + filename)):
            print('\033[92m' + '- ' + filename + ' saved in ' + subdir + '.' + '\033[0m')
        else:
            print('\033[91m' + '- Error!' + '\033[0m')
            some_error = True

    return some_error

def download_iiif_files_from_manifest(manifest_name, maindir, firstpage = 1, lastpage = -1, use_page_numbers = False):
    if(is_url(manifest_name)):
        d = json.loads(open_url(manifest_name))
    else:
        with open(manifest_name) as f:
            d = json.load(f)
    #print(json.dumps(d, indent=4))

    # Read manifest
    title, labels, iiif_ids, iiif_formats, iiif_w, iiif_h = read_iiif_json(d)
    print('- Title: ' + title)
    print('- Files: ' + str(len(labels)))

    # Create subdirectory from title
    subdir = maindir + '/' + sanitize_name(title)
    if os.path.exists(subdir):
        rmtree(subdir)
    os.mkdir(subdir)

    # Download images from url
    some_error = download_iiif_files(iiif_ids, labels, iiif_formats, iiif_w, iiif_h, subdir, firstpage, lastpage, use_page_numbers)

    # Rename directory if something was wrong
    if(some_error):
        err_subdir = maindir + '/' + 'ERR_' + title
        if os.path.exists(err_subdir):
            rmtree(err_subdir)
        os.rename(subdir, err_subdir)
        print('\033[91m' + 'Some error with ' + title + '.\033[0m') 
