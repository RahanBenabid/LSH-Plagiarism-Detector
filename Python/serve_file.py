#!/usr/bin/env python3

def read_content(file_name):
	file_name = ('./documents/' + file_name)
	with open(file_name, "r") as file:
		return file.read()