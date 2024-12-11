#!/usr/bin/env python3

import os
import re

def rename_files(folder_path):
    # get all .txt files
    txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]
    
    # create a list to store file paths with their original names
    file_list = []
    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)
        file_list.append((filename, file_path))
    
    # sort the files to determine the order
    file_list.sort(key=lambda x: x[0])
    
    # rename files sequentially
    for new_index, (old_filename, file_path) in enumerate(file_list, start=1):
        new_filename = f'essay{new_index}.txt'
        new_file_path = os.path.join(folder_path, new_filename)
        
        # only rename if the filename has changed
        if old_filename != new_filename:
            os.rename(file_path, new_file_path)

rename_files("./documents/")