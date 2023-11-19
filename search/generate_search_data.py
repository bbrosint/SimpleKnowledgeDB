################################################
#                                              #
#  Script for generating search data           #
#  (indexing all *.md files of a given path)   #
#  for the Simple Knowledge DB                 #
#                                              #
################################################

from glob import glob
from datetime import datetime as dt
import json
import argparse


def extract_metadata(filepath):
    header_info = {'author':'','created':'','changed':'','tags':[], 'title':''}
    header_started = False
    count = 0
    parameter_entry_count = 4
    with open(filepath,'r') as kdbf_stream:
        for line in kdbf_stream:
            stripped_line = line.strip()
            if header_started and count<parameter_entry_count:
                count +=1
                param = stripped_line.split(':')
                if param[0] in header_info.keys():
                    header_info[param[0]] = param[1].strip()
                    if param[0] == 'created' or param[0]=='changed':
                        header_info[param[0]] = dt.fromisoformat(param[1].strip()).timestamp()*1000
                    if param[0] == 'tags':
                        header_info[param[0]] = [i.strip() for i in param[1].split(',')]
            if stripped_line == '---' and not header_started:
                header_started = True
            if line[:2] == '# ':
                header_info['title'] = line[2:].strip()
                break
    header_info['filepath'] = filepath.split('/')[-1].split('\\')[-1]  
    header_info['id'] = id(header_info)
    return header_info

def generate_search_dict(kdb_metadata):
    search_data = {'tags':{},'titles':{},'authors':{},'items':{}}
    for item in kdb_metadata:    
        author = item['author']
        kdb_id = item['id']
        search_data['items'][kdb_id] = item
        search_data['items'][kdb_id].pop('id')
        title = item['title']
        tags = []
        [tags.extend(i.split(' ')) for i in item['tags']]
        if not author in search_data['authors']:
            search_data['authors'][author] = []
        if not kdb_id in search_data['authors'][author]:
            search_data['authors'][author].append(kdb_id)
        if not title in search_data['titles']:
            search_data['titles'][title] = []
        if not kdb_id in search_data['titles'][title]:
            search_data['titles'][title].append(kdb_id)
        for tag in tags:
            if not tag in search_data['tags']:
                search_data['tags'][tag] = []
            if not kdb_id in search_data['tags'][tag]:
                search_data['tags'][tag].append(kdb_id)
    return search_data        

def output_search_data(search_data):
    json_data = json.dumps(search_data)
    with open('./data.json','w') as js_stream:
        js_stream.write(f'jsonCallback({json_data});')

def main(args):
    kdocs = 'knowledgedocs/'
    main_filepath = f'../{kdocs}'
    md_filepath = f'../{kdocs}'
    if args.docpath:
        main_filepath = args.docpath
        if not main_filepath[-1] == '/':
            main_filepath += '/'
    if args.input:
        md_filepath = args.input
        if not md_filepath[-1] == '/' or md_filepath[-1] == '\\':
            md_filepath += '/'
        
            

    md_filepath += '*.md'
    knowledge_db_files = glob(md_filepath)
    kdb_metadata = [extract_metadata(i) for i in knowledge_db_files]
    search_data = generate_search_dict(kdb_metadata)
    search_data['main_path'] = main_filepath
    output_search_data(search_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-d', '--docpath')
    args = parser.parse_args()
    main(args)