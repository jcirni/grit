#import numpy as np
import pandas as pd
import argparse
import os.path
import re
pd.set_option('display.width', 120) 

#catch bad file path
def valid_file(arg):
	if not os.path.isfile(arg):
		parser.error("File does not exist!")
	else:
		return arg

#standard outputs for data validation
def err_data(value, row, col):
	raise ValueError("Your value, " + value + ", at row %d and col %d does not contain appropriate data" % (row, col) )

#test chrom data
def valid_chrom(chrom):
	if chrom[0:3] == 'chr' and int(chrom[3:]) < 23:
		return True
	else:
		return False

#test start position
def valid_start_position(value):
	if 0 < value and value < (2 ** 32 + 1):
		return True
	else:
		return False

#test end position		
def valid_end_position(end, start):
	 if 0 < end  and end < (2 ** 32 + 1) and start < end:
	 	return True
	 else:
	 	return False

#test feature name
def valid_feature_name(feature):
	if re.match("^[\w_()-]*$", feature):
		return True
	else:
		return False

#validate data set
def valid_data(data, length):
	#validate chrom field
	i = 0
	while i < length:
		if valid_chrom(data.iloc[i][0]):
			#cut chr prefix and update value
			data.set_value(i,0, (data.iloc[i][0])[3:], takeable=True)
			i += 1
		else:
			err_data(data.iloc[i][0],i,0)
	print "chrom field reported no errors!"
	#validate start position
	i = 0
	while i < length:
		if valid_start_position(data.iloc[i][1]):
			i += 1
		else:
			err_data(data.iloc[i][1],i,1)
	print "start position field reported no errors!"
	#validate end position
	i = 0
	while i < length:
		if valid_end_position(data.iloc[i][2], data.iloc[i][1]):
			i += 1
		else:
			err_data(data.iloc[i][2],i,2)
	print "end position field reported no errors!"
	#validate feature name
	i = 0
	while i < length:
		if valid_feature_name(data.iloc[i][3]):
			i += 1
		else:
			err_data(data.iloc[i][3],i,3)
	print "feature name field reported no errors!"
	#validate strand 
	i = 0
	while i < length:
		if data.iloc[i][4] == '-' or data.iloc[i][4] == '+':
			i += 1
		else:
			err_data(data.iloc[i][4],i,4)
	print "strand field reported no errors!"

	return True

def get_user_chrom():
	opt = raw_input("Enter chromosome value (format chr##): ")
	if valid_chrom(opt):
		return int(opt[3:])
	else:
		print "invalid input, please try again"
		get_user_chrom()

def get_user_pos():
	opt = raw_input("OPTIONAL: Enter position value. Must be a number 1 - 2^32. Or enter no: ")
	if opt == 'no' or opt =='No' or opt == 'n':
		return None
	else:
		try:
			opt = int(opt)
			if valid_start_position(opt):
				return opt
		except ValueError:
			print "invalid input, value must be 1 - 2^32. Please try again"
			get_user_pos()

def get_user_feature():
	opt = raw_input("Enter feature name: ")
	if valid_feature_name(opt):
		return opt
	else:
		print "invalid input, please try again"
		get_user_feature()

#queries dataset for chromosome 	
def search_for_chrom(data, chrom, pos):
	if pos == None:
		return data.loc[data['chromosome'] == chrom]
	else:
		return data.loc[(data['chromosome'] == chrom) & (data['start_pos'] < pos) & (data['end_pos'] > pos)]

#queries dataset for feature
def search_for_feature(data, feature):
	return data.loc[data['feature_name'] == feature]

#summary metrix
def get_metrics():
	print
	print "================== Your Metrics ======================"
	print
	#count unique features per chromosome by chromosome and starting position
	print "Features in data set: %d" % len(df.groupby(['chromosome', 'start_pos']).size().index)
	#new length column
	df['length'] = df['end_pos'] - df['start_pos']
	#min
	print "The smallest length is: %d" % df['length'].min()
	#max
	print "The largest length is: %d" % df['length'].max()
	#mean
	print "The average length is: %d" % df['length'].mean()
	#count unique features per strand
	print
	print "==== Features per Strand ===="
	print
	print df.groupby(['chromosome', 'strand']).size()
	
#get user's next action
def get_user_input():
	opta = raw_input("Query data, get stats, or exit? (q/s/x): ")
	if opta == 'q':
		optb = raw_input("Search by pos or feat? (pos/feat): ")
		if optb == 'pos':
			print search_for_chrom(df, get_user_chrom(), get_user_pos())
			get_user_input()
		elif optb == 'feat':
			print search_for_feature(df, get_user_feature())
			get_user_input()
		else:
			print "invalid input please try again (pos/feat): "
			get_user_input()
	elif opta == 's':
		get_metrics()
		get_user_input()
	elif opta == 'x':
		print "All done."
		exit()
	else:
		print "invalid input, please try again"
		get_user_input()

#command line arguments
parser = argparse.ArgumentParser(description='Parses genetic annotation data and allows querying with command line arguments. Requires file (-f /path/to/file)')
parser.add_argument('-f', '--file', type=str, help='path to file')

#parse arguments
args = parser.parse_args()
#check for valid file and read file
if args.file:
	print "Validating data now!"
	df = pd.read_csv(valid_file(args.file), '\t' , header=None)
	df.columns = ['chromosome', 'start_pos', 'end_pos', 'feature_name', 'strand']
	print
	
	if valid_data(df, len(df.index)):
		print "Data validation complete!"
		#now that data is good, strip chr prefix from chrom column
		df[['chromosome']] = df[['chromosome']].apply(pd.to_numeric)
	print df
	#what does user want to do now?
	get_user_input()
else:
	print parser.description



