import json
import time
import os
from shutil import rmtree
from urllib.request import urlopen, Request

class Conf:
    def __init__(self, firstpage = 1, lastpage = -1, use_labels = False, force = False):
        self.firstpage = firstpage
        self.lastpage = lastpage
        self.use_labels = use_labels
        self.force = force

class Info:
    def __init__(self, label, iiif_id, iiif_format, iiif_w, iiif_h):
        self.label = label
        self.id = iiif_id
        self.format = iiif_format
        self.w = iiif_w
        self.h = iiif_h

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
    except Exception as err:
        print(Exception, err)
        #print(res.getcode())
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

def sanitize_name(title):
    title = title.replace("/", " ")
    title = title.replace(":", "")
    return title

def read_iiif_manifest2(d):
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

    manifest_label = d.get('label')
    if(manifest_label == None): raise Exception

    manifest_id = d.get('@id')
    if(manifest_id == None): raise Exception

    # Read sequences
    sequences = d.get('sequences')
    if(sequences == None): raise Exception
    # Assumption #1: 1 sequence in sequences
    sequence = sequences[0]
    #if(sequence.get("@type") != 'sc:Sequence'): raise Exception

    # Read canvases
    canvases = sequence.get("canvases")

    infos = []
    for c in canvases:
        #if(c.get("@type") != 'sc:Canvas'): raise Exception
        label = c.get("label")

        # Read images
        # Assumption #2: 1 image in images
        i = c.get("images")[0]
        #if(i.get('@type') != "oa:Annotation"): raise Exception
        #if((i.get('motivation')).lower() != "sc:painting"): raise Exception
        iiif_w = c.get('width')
        iiif_h = c.get('height')

        # Read resource
        resource = i.get("resource")
        # "The image MUST have an @id field [...] Its media type MAY be listed in format"
        iiif_id = resource.get('@id')
        if(iiif_id == None): raise Exception
        iiif_format = resource.get('format', 'NA')

        infos.append(Info(label, iiif_id, iiif_format, iiif_w, iiif_h))

    return manifest_label, manifest_id, infos

def read_iiif_manifest3(d):
    # - label
    # - id
    # - items (type: Canvas):
    #   - label
    #   - items (type: AnnotationPage):
    #     - items (type: Annotation):
    #       - body:
    #         - id
    #         - format
    #         - width
    #         - height

    manifest_label = d.get('label')
    if(manifest_label == None): raise Exception
    if(isinstance(manifest_label, dict)):
        manifest_label = next(iter(manifest_label.values())) # take first value
    manifest_label = manifest_label[0]

    manifest_id = d.get('id')
    if(manifest_id == None): raise Exception

    # Read canvas
    items = d.get('items')
    #if(items == None): raise Exception
    infos = []
    for i in items:
        #if(i.get('type') != "Canvas"): raise Exception
        l = i.get('label', 'NA')
        if(isinstance(l, dict)):
            l = next(iter(l.values())) # take first value
        l = l[0]

        if(len(i.get('items')) == 0):
            infos.append(Info(l, 'NA', 'NA', 0, 0))
        else:
            # Read annotation page
            # Assumption #1: 1 annotation page in canvas
            annotation_page = i.get('items')[0]

            # Read annotation
            #if(annotation_page.get('type') != "AnnotationPage"): raise Exception
            # Assumption #2: 1 annotation in annotation page
            annotation = annotation_page.get('items')[0]
            #if(annotation.get('type') != "Annotation"): raise Exception

            # Read body
            iiif_id = annotation.get('body').get('id')
            iiif_format = annotation.get('body').get('format')
            iiif_w = annotation.get('body').get('width')
            iiif_h = annotation.get('body').get('height')

            infos.append(Info(l, iiif_id, iiif_format, iiif_w, iiif_h))

    return manifest_label, manifest_id, infos

def download_iiif_files_from_manifest(api, d, maindir, conf = Conf()):
    # Read manifest
    if(api == 2):
        manifest_label, manifest_id, infos = read_iiif_manifest2(d)
    elif(api == 3):
        manifest_label, manifest_id, infos = read_iiif_manifest3(d)

    # Print manifest feautures
    print('- Manifest ID: ' + manifest_id)
    print('- Title: ' + manifest_label)
    print('- Files: ' + str(len(infos)))

    if(len(infos) > 0):
        # Create subdirectory from manifest label
        subdir = maindir + '/' + sanitize_name(manifest_label)
        if (not os.path.exists(subdir)):
            os.mkdir(subdir)
    
        # Read configuration parameters
        firstpage = conf.firstpage
        lastpage = conf.lastpage
        use_labels = conf.use_labels
    
        # Create sub-array (firstpage, lastpage)
        totpages = len(infos)
        if(firstpage != 1 or lastpage != -1):
            infos = infos[firstpage-1:]
            infos = infos[:lastpage-firstpage+1]
            print("- Downloading pages " + str(firstpage) + "-" + str(lastpage) + " from a total of " + str(totpages))
    
        # Loop over each id
        some_error = False
        try_with_id = True
        total_filesize = 0
        start_time = time.time()
        downloaded_cnt = 0
        for cnt, info in enumerate(infos):
            percentage = round((cnt + 1) / len(infos) * 100, 1)
            cnt = cnt + firstpage - 1
    
            # Print counters and label
            print('[n.' + str(cnt + 1) + '/' + str(totpages) + '; '  + str(percentage) + '%] Label: ' + info.label)
    
            # Print file ID
            print('- ID: ' + info.id)
            if(info.id == 'NA'):
                continue
   
            # Print file extension
            ext = get_extension(info.format)
            if(ext == 'NA' and '.' in info.id):
                ext = '.' + info.id.split('.')[-1] # if format not defined, try take ext from file name
            print('- Format: ' + info.format + ' => Extension: ' + ext)
    
            # Print file size
            print('- Width: '  + str(info.w) + ' px')
            print('- Height: ' + str(info.h) + ' px')
    
            # Download file
            if(use_labels):
                filename = sanitize_name(info.label) + ext
            else:
                filename = 'p' + str(cnt + 1).zfill(3) + ext
            if(os.path.exists(subdir + '/' + filename) and not conf.force):
                print('- ' + subdir + '/' + filename + " exists, skip.")
                continue

            # Priority to image id, but if it doesn't work we move
            # to URI template and we stop trying with it
            filesize = -1
            if(try_with_id): 
                filesize = download_file(info.id, subdir + '/' + filename)
                if(filesize <= 0):
                    print("- Cannot download " + info.id)
                    try_with_id = False

            if(filesize <= 0):
                img_url = get_img_url(info.id, ext)
                filesize = download_file(img_url, subdir + '/' + filename)
    
            if(filesize <= 0):
                print('\033[91m' + '- Error!' + '\033[0m')
                some_error = True
            else:
                print('\033[92m' + '- ' + filename + ' (' + str(round(filesize / 1000)) + ' KB) saved in ' + subdir + '.' + '\033[0m')
                total_filesize += filesize
                downloaded_cnt = downloaded_cnt + 1
 
        end_time = time.time()

        # Print some statistics    
        print("--- Stats ---")
        print("- Downloaded files: " + str(downloaded_cnt))
        total_time = (end_time - start_time)
        print("- Elapsed time: " + str(round(total_time)) + " s")
        if(downloaded_cnt > 0):
            print("- Avg time/file: " + str(round(total_time/downloaded_cnt)) + " s")
            print("- Disc usage: " + str(round(total_filesize/1024)) + " KB")
            print("- Avg file size: " + str(round(total_filesize/(downloaded_cnt * 1024))) + " KB")
        print("-------------")
 
        # Rename directory if something was wrong
        if(some_error):
            err_subdir = maindir + '/' + 'ERR_' + sanitize_name(manifest_label)
            if os.path.exists(err_subdir):
                rmtree(err_subdir)
            os.rename(subdir, err_subdir)
            print('\033[91m' + 'Some error with ' + sanitize_name(manifest_label) + '.\033[0m') 

def download_iiif_files(input_name, maindir, conf = Conf()):
    # Check if input is a file or an url and open it
    if(is_url(input_name)):
        d = json.loads(open_url(input_name).read())
    else:
        with open(input_name) as f:
            d = json.load(f)

    # Check API version and define json dictionary elements accordingly
    context = d['@context']
    if(context.endswith('2/context.json')):
        api = 2
        type_key = '@type'
        manifest_string = 'sc:Manifest'
        collection_string = 'sc:Collection'
        manifests_key = 'manifests'
        id_key = '@id'
    elif(context.endswith('3/context.json')):
        api = 3
        type_key = 'type'
        manifest_string = 'Manifest'
        collection_string = 'Collection'
        manifests_key = 'items'
        id_key = 'id'
    else:
        raise Exception("Unsupported API (context: " + context + ')')

    # Check if input file is manifest or a collection
    iiif_type = d.get(type_key)
    if(iiif_type == manifest_string):
        download_iiif_files_from_manifest(api, d, maindir, conf)
    elif(iiif_type == collection_string):
        # TODO: one directory for same collection?
        manifests = d.get(manifests_key)
        for m in manifests:
            manifest_id = m.get(id_key)
            d = json.loads(open_url(manifest_id).read())
            download_iiif_files_from_manifest(api, d, maindir, conf)
    else:
        raise Exception("Not a manifest or a collection of manifests (type: " + iiif_type + ')')
