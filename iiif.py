import json
import time
import os
from shutil import rmtree
from urllib.request import urlopen, Request

# Doc:
# - Presentation: https://iiif.io/api/presentation/2.0/
# - Image: https://iiif.io/api/image/2.0/

class Conf:
    def __init__(self, firstpage = 1, lastpage = -1, use_labels = False, force = False):
        self.firstpage = firstpage
        self.lastpage = lastpage
        self.use_labels = use_labels
        self.force = force

class Info:
    def __init__(self, manifest_id, title, labels, iiif_ids, iiif_formats, iiif_w, iiif_h):
        self.manifest_id = manifest_id
        self.title = title
        self.labels = labels
        self.iiif_ids = iiif_ids
        self.iiif_formats = iiif_formats
        self.iiif_w = iiif_w
        self.iiif_h = iiif_h

def open_url(u):
    headers = {'User-Agent' : "Mozilla/5.0"}
    try:
        response = urlopen(Request(u, headers = headers), timeout = 30)
        return response
    except Exception as err:
        print(Exception, err)
        return;

def download_file(u, filepath):
    u = u.replace(" ", "%20")
    print("- Downloading " + u)
    try:
        res = open_url(u)
        #print(response.getcode())
    except Exception as err:
        print(Exception, err)
        return -1
  
    #file_size = res.headers['Content-Length']
    #print('- ' + str(file_size) + ' bytes')
  
    # Create the file (binary) mode even when it exists
    with open(filepath, 'wb') as file:
        try:
            file.write(res.read())
            file_size = os.path.getsize(filepath)
            return file_size
        except Exception as err:
            print(Exception, err)
            os.remove(filepath)
            return -1

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
    return mime_to_extension.get(mime_type, 'NA')

def get_img_url(iiif_id, ext, region = 'full', size = 'max', rotation = '0', quality = 'default'):
    return iiif_id + '/' + region + '/' + size + '/' + rotation + '/' + quality + ext

def read_iiif2_manifest(d):
    # - label
    # - @id
    # - sequences:
    #   - canvases:
    #     - label
    #     - width
    #     - height
    #     - images (content):
    #       - resource:
    #         - @id
    #         - format

    title = d['label']
    manifest_id = d['@id']

    sequences = d["sequences"]
    # Assumption #1: 1 sequence in sequences
    sequence = sequences[0]
    #if(sequence.get("@type") != 'sc:Sequence'): raise Exception

    canvanses = sequence.get("canvases")

    labels = []
    images = []
    iiif_w = []
    iiif_h = []
    for c in canvanses:
        #if(c.get("@type") != 'sc:Canvas'): raise Exception
        labels.append(c.get("label"))
        # Assumption #2: 1 image in images
        images.append(c.get("images")[0])
        iiif_w.append(c.get('width'))
        iiif_h.append(c.get('height'))

    resources = []
    for i in images:
        #if(i.get('@type') != "oa:Annotation"): raise Exception
        if((i.get('motivation')).lower() != "sc:painting"): # lower for "sc:Painting"
            continue
        resources.append(i.get("resource"))

    iiif_ids = []
    iiif_formats = []
    for r in resources:
        iiif_ids.append(r.get('@id'))
        iiif_formats.append(r.get('format', 'NA'))

    if(len(labels) != len(iiif_ids)):
        raise Exception("len discrepancy") 

    return Info(manifest_id, title, labels, iiif_ids, iiif_formats, iiif_w, iiif_h)

def read_iiif_manifest(d):
    context = d['@context']
    if(context.endswith('2/context.json')):
        iiif_type = d.get('@type')
        if(iiif_type != 'sc:Manifest'):
            raise Exception("Not a manifest (type: " + iiif_type + ')') 
        return read_iiif2_manifest(d)
    else:
        # TODO Other standars
        raise Exception("Only IIIF 2.0 is supported today (context: " + context + ')') 

def sanitize_name(title):
    title = title.replace("/", " ")
    title = title.replace(":", "")
    return title

def download_iiif_files(info, subdir, conf = Conf()):
    # Read IIIF info
    iiif_ids = info.iiif_ids
    labels = info.labels
    iiif_formats = info.iiif_formats
    iiif_w = info.iiif_w
    iiif_h = info.iiif_h

    # Read configuration parameters
    firstpage = conf.firstpage
    lastpage = conf.lastpage
    use_labels = conf.use_labels

    # Create sub-array
    totpages = len(iiif_ids)
    if(firstpage != 1 or lastpage != -1):
        iiif_ids = iiif_ids[firstpage-1:]
        iiif_ids = iiif_ids[:lastpage-firstpage+1]
        print("- Downloading pages " + str(firstpage) + "-" + str(lastpage) + " from a total of " + str(totpages))

    # Loop over each id
    some_error = False
    total_filesize = 0
    start_time = time.time()
    for cnt, iiif_id in enumerate(iiif_ids):
        percentage = round((cnt + 1) / len(iiif_ids) * 100, 1)
        cnt = cnt + firstpage - 1

        # Print counters and label
        print('[n.' + str(cnt + 1) + '/' + str(totpages) + '; '  + str(percentage) + '%] Label: ' + labels[cnt])

        # Print file ID
        print('- ID: ' + iiif_id)

        # Print file extension
        ext = get_extension(iiif_formats[cnt])
        if(ext == 'NA' and '.' in iiif_id):
          ext = '.' + iiif_id.split('.')[-1] # if format not defined, try take ext from file name
        print('- Format: ' + iiif_formats[cnt] + ' => Extension: ' + ext)

        # Print file size
        print('- Width: ' + str(iiif_w[cnt]) + ' px')
        print('- Height: ' + str(iiif_h[cnt]) + ' px')

        # Download file
        if(use_labels):
            filename = sanitize_name(labels[cnt]) + ext
        else:
            filename = 'p' + str(cnt + 1).zfill(3) + ext
        if(os.path.exists(subdir + '/' + filename) and not conf.force):
            print('- ' + subdir + '/' + filename + " exists, skip.")
            continue;

        img_url = get_img_url(iiif_id, ext)
        filesize = download_file(img_url, subdir + '/' + filename)
        if(filesize <= 0):
            filesize = download_file(iiif_id, subdir + '/' + filename)

        if(filesize <= 0):
            print('\033[91m' + '- Error!' + '\033[0m')
            some_error = True
        else:
            print('\033[92m' + '- ' + filename + ' (' + str(round(filesize / 1000)) + ' KB) saved in ' + subdir + '.' + '\033[0m')
            total_filesize += filesize

    end_time = time.time()

    # TODO: distinguish downloaded and manifest files counts
    print("--- Stats ---")
    print("- Files: " + str(len(iiif_ids)))
    total_time = (end_time - start_time)
    print("- Elapsed time: " + str(round(total_time)) + " s")
    print("- Avg time/file: " + str(round(total_time/len(iiif_ids))) + " s")
    print("- Disc usage: " + str(round(total_filesize/1024)) + " KB")
    print("- Avg file size: " + str(round(total_filesize/(len(iiif_ids) * 1024))) + " KB")
    print("-------------")

    return some_error

def download_iiif_files_from_manifest(manifest_name, maindir, conf = Conf()):
    if(is_url(manifest_name)):
        d = json.loads(open_url(manifest_name).read())
    else:
        with open(manifest_name) as f:
            d = json.load(f)

    # Read manifest
    info = read_iiif_manifest(d)

    print('- Manifest ID: ' + info.manifest_id)
    print('- Title: ' + info.title)
    print('- Files: ' + str(len(info.labels)))

    if(len(info.labels) > 0):
        # Create subdirectory from title
        subdir = maindir + '/' + sanitize_name(info.title)
        if (not os.path.exists(subdir)):
            os.mkdir(subdir)
    
        # Download images from url
        some_error = download_iiif_files(info, subdir, conf)
    
        # Rename directory if something was wrong
        if(some_error):
            err_subdir = maindir + '/' + 'ERR_' + info.title
            if os.path.exists(err_subdir):
                rmtree(err_subdir)
            os.rename(subdir, err_subdir)
            print('\033[91m' + 'Some error with ' + info.title + '.\033[0m') 
