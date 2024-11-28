#!/usr/bin/env python3

import os

def rename_files(folder_path):
	entries = os.listdir(folder_path)
	
	# to filter .txt  files
	txt_files = [file for file in entries if file.endswith('.txt')]
	
	for index, current_name in enumerate(txt_files, start=1):
		new_name = f'essay{index}.txt'
		
		current_file_path = os.path.join(folder_path, current_name)
		new_file_path = os.path.join(folder_path, new_name)
		
		os.rename(current_name, new_file_path)

rename_files("./documents/")