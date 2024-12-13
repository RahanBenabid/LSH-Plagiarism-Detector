#!/usr/bin/env python3

def change_main(content):
	file = './main.txt'
	with open(file, 'w') as f:
		f.write(content)
		
