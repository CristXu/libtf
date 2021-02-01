import os 
import urllib.request as urllib2
import json 
from contextlib import closing
import time 

keil_scripts = 'generate_keil_project.py' #r'C:\Users\nxf48054\Desktop\share\tensorflow\tensorflow\lite\micro\tools\make\generate_keil_project.py'

def readUrl(url):
    with closing(urllib2.urlopen(url)) as ufo:
        return ufo.read().decode("utf-8")

USE_MAKE = 1
def find_file(file_name):
    searching_key = file_name.split('.')[0]
    content = readUrl("http://192.168.175.1:80/?search={0}&json=1&path_column=1&sort=path".format(urllib2.quote(searching_key)))
    results = json.loads(content, encoding='utf-8')
    src_full_path = []
    hrd_full_path = []
    already_in = []
    for r in results['results']:
        name = r['name']    
        n,ext =  os.path.splitext(name)
        if USE_MAKE or (searching_key == n) and (not (name in already_in)):
            if (not ('Python' in r['path'])) and ('lite' in r['path']) and (not ('gpu' in r['path'])):
                if (ext in ['.c', '.cc']):
                    src_full_path += [' ' + r['path'].replace('\\', '/') + '/' + name]
                    header = r['path'].replace('\\', '/') + '/' + n + '.h'
                    if os.path.exists(header):
                        hrd_full_path += [' ' + header]
                already_in += [name]
    return [src_full_path, hrd_full_path]

class ARGS():
    def __init__(self, args_list):
        self.input_template = args_list[0].replace(' --input_template ', '')
        self.output_file = args_list[1].replace(' --output_file ', '')
        self.executable = args_list[2].replace(' --executable ', '')
        self.hdrs = args_list[3].replace(' --hdrs', '')
        self.srcs = args_list[4].replace(' --srcs', '')
        self.include_paths = args_list[5].replace(' --include_paths', '')
        self.defines = args_list[6].replace(' --defines','')


prefix = 'C:/Users/nxf48054/Desktop/share/tensorflow'
def get_include_path():
    # from the make linux
    with open('include.txt') as f:
        headers = f.read()
    headers = headers.replace('-I', prefix + '/')  
    return headers  

def get_defines():
    # from the make linus 
    with open('defines.txt') as f:
        defines = f.read()
    defines = defines.replace('-D', '')
    return ' ' + defines

if __name__ == "__main__":
    INPUT_TEMPLATE = ' --input_template ./keil_project_rt1170.uvprojx.tpl'
    OUTPUT_FILE = ' --output_file ./libtf.uvprojx'
    EXECUTABLE = ' --executable libtf'
    HDRS = ' --hdrs ./libtf.h'
    SRCS = ' --srcs ./libtf.cc C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/openmvcam/debug_log.cc ' \
           ' C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/kernels/transpose_conv.cc' \
           ' C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/kernels/fully_connected_common.cc' \
           ' C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/kernels/softmax_common.cc' \
           ' C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/kernels/svdf_common.cc' \
           ' C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/kernels/quantize_common.cc ' \
           #' C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/kernels/transpose.cc '
 
    INCLUDE_PATH = ' --include_paths'
    DEFINES = ' --defines'

    INCLUDE_PATH += get_include_path()
    DEFINES += get_defines()
    
    f_write = open('file_names.txt', 'w')
    # keil's erro log if include *.a
    miss_file = open('miss_files.txt')
    not_in = open('not_in.txt', 'w')
    miss_names = [l.split('.o ')[0].split(' ')[-1]+'.c' for l in miss_file.readlines() if '.o ' in l]
    length = len(miss_names)
    if USE_MAKE:
        f = open('source_name_2.txt')
        all_lines = [i.split('obj')[-1] for i in f.read().split(' ')]
        key = '.o'
    else:
        # arm-none-eabi-objdump *.a > source_name.txt
        f = open('source_name.txt')
        all_lines = f.readlines()
        key = '.o:'
    for line in all_lines:
        if key in line:
            if USE_MAKE:
                src_file = prefix + line.replace('.o', '.c')
                path = [' ' + src_file] if os.path.exists(src_file) else [' ' + src_file.replace('.c', '.cc')]
                h_file = prefix + line.replace('.o', '.h')
                if os.path.exists(h_file):
                    path.append(' ' + h_file)
                else:
                    path.append('')
                split_name = src_file
            else:
                split_name =  line.split('.o:')[0]+'.c'
                print(split_name)
                path = find_file(split_name)
            SRCS += ''.join(path[0])
            HDRS += ''.join(path[1])
            f_write.write(split_name + '\n')
            if split_name in miss_names: miss_names.remove(split_name)
    for item in miss_names:
        not_in.write(item + '\n')
    not_in.write('All %d, miss %d, same %d'%(length, len(miss_names), length-len(miss_names)))
    not_in.close()
    f_write.close()

    cmd = [INPUT_TEMPLATE, OUTPUT_FILE, EXECUTABLE, HDRS, SRCS, INCLUDE_PATH, DEFINES]
    if len(SRCS) < 255:
        os.system(keil_scripts + ''.join(cmd))
    else:
        from generate_keil_project import main
        main(None, ARGS(cmd))

    # for the person detect project 
    INPUT_TEMPLATE = ' --input_template ./keil_project_rt1170.uvprojx.tpl'
    OUTPUT_FILE = ' --output_file ./person_detect.uvprojx'
    EXECUTABLE = ' --executable libtf_person_detect_model_data'
    HDRS = ' --hdrs C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/tools/make/downloads/person_model_grayscale/person_detect_model_data.h'
    SRCS = ' --srcs C:/Users/nxf48054/Desktop/share/tensorflow/tensorflow/lite/micro/tools/make/downloads/person_model_grayscale/person_detect_model_data.cc'
    INCLUDE_PATH = ' --include_paths C:/Users/nxf48054/Desktop/share/tensorflow'
    DEFINES = ' --defines CM7'
    cmd = [INPUT_TEMPLATE, OUTPUT_FILE, EXECUTABLE, HDRS, SRCS, INCLUDE_PATH, DEFINES]
    os.system(keil_scripts + ''.join(cmd))

