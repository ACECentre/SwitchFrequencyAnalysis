import click
import csv
import os.path
import re

@click.command()
@click.option('--ssteps', type=click.Path(exists=True), default='scan-steps-lib/ssteps-eardu.csv', help='Path to a csv of your scan steps')
@click.option('--scanrate', default=1000, help='Scan rate in ms')
@click.option('--output-type', default='all', help='All, Lesher, Damper, Steps, Hits, show-workings, show-predictions, csv-all')
@click.option('--ignore-spaces', default=True, type=bool, help='Ignore spaces? Useful if you have no space in your layout')
@click.option('--ignore-predictions', default=False, type=bool, help='Ignore predictions? i.e. ignore anything uppercased')
@click.option('--prediction-time', default=0, help='How long does it take the person to select a prediction on average? in ms. NB: Ignored if ignored-predictions is True')
@click.option('--sentence', prompt='Test sentence:',
				help='Enter your test sentence here')

def stepcount(ssteps, scanrate, ignore_spaces , ignore_predictions, prediction_time, sentence, output_type):
	"""Takes a switch step count and a sentence and display number of steps to get there"""
	letterfreq = dict()
	sum = t_lesher = t_damper = sum_pred_letters = sum_pred_words = sum_words = 0
	show_workings = ''
	# remove dodgy chars
	# Bad code. Could do this a lot better if I spent 5 minutes 
	s_filtered = re.sub(r"[0-9]+", '', sentence)
	s_filtered = re.sub(r"#+", '', s_filtered)
	s_filtered = re.sub(r"'+", '', s_filtered)
	s_filtered = re.sub(r"\/+", '', s_filtered)

	# predictions?
	for word in s_filtered.split():
		len_ucase_str = len(re.findall(r'[A-Z]',word))
		sum_pred_letters = sum_pred_letters + len_ucase_str
		sum_pred_words = sum_pred_words +1 if len_ucase_str > 0  else sum_pred_words
	
	# ignore predictions?
	if ignore_predictions:
		s_filtered = re.sub(r"[A-Z]+", '', s_filtered)

	s_filtered = s_filtered.lower()
	
	#calc word count
	sum_words = len(re.findall(r"\s+",s_filtered))+1
	
	# ignore spaces?
	if ignore_spaces:
		s_filtered = re.sub(r"\s+", '', s_filtered)
	else:
		s_filtered = re.sub(r"\s+", '_', s_filtered)


	
	strlen = len(s_filtered)
			
	if os.path.isfile(ssteps):
		with open(ssteps, 'rt') as f:
			reader = csv.DictReader(f)
			for row in reader:
				letterfreq[row['Letter']]=row['Scan Steps']
		# Now we have the letter freq chart lets do our sums on this with our test sentences
		for n in s_filtered:
			sum = sum + float(letterfreq[n])
			t_lesher = t_lesher + ((float(letterfreq[n])+2)*scanrate)
			t_damper = t_damper + ((float(letterfreq[n])+1)*scanrate)
			show_workings = show_workings + n +' ' + letterfreq[n] + ', '
		
		if ignore_predictions == False :
			t_lesher = t_lesher + sum_pred_words * prediction_time
			t_damper = t_damper + sum_pred_words * prediction_time
			show_workings = show_workings +  ' AND add sum of predicted words ('+ str(+sum_pred_words)+') * prediction_time (' + str(prediction_time) + ')'
				
		if ('csv-all' in output_type):
			# print a csv of all data.. 
			# headers = 'steps, hits, lesher (ms), damper (ms), no-hit (ms), predicted words, predicted letters, wordcount
			csv_line = str(sum) + ',' + str(strlen*2) + ',' + str(t_lesher) + ',' + str(t_damper) + ',' + str((sum)*scanrate) + ',' + str(sum_pred_words) + ',' + str(sum_pred_letters) + ',' + str(sum_words)
			print(csv_line)			
		
		if ('Stats' in output_type or output_type == 'all'):		
			print('Full steps:'+str(sum))
			# ss  100 (nb  na)/nb
			# nb - scan steps. na = augmented switch count.
			# 2 hits per letter. Its always that way
			print('Switch hits (auto scan - auto start):'+str(strlen*2))
		if (('Lesher' in output_type) or (output_type == 'all')):
			print('Lesher time (H:M:S.ms), '+mstotime(t_lesher))
		if ('Damper' in output_type or output_type == 'all'):
			print('Damper time (H:M:S.ms), '+mstotime(t_damper))
		if ('No-Hit' in output_type or output_type == 'all'):
			print('No hit time (H:M:S.ms), '+mstotime((sum)*scanrate))
		if ('show-predictions' in output_type or output_type == 'all'):
			print('No. of predicted words '+ str(sum_pred_words))
			print('No. of predicted letters '+ str(sum_pred_letters))
		if ('show-workings' in output_type or output_type == 'all'):
			show_workings = 'string: ' + s_filtered + ' -> ' + show_workings + ' = Total steps of '+ str(sum) + '. Lesher Time = Σ (each step + 2) * scanrate (i.e. '+ str(scanrate) + ')'
			if ignore_predictions == False :
				show_workings = show_workings +  ' AND add sum of predicted words ('+ str(+sum_pred_words)+') * prediction_time (' + str(prediction_time) + ')'
			print('Show workings:'+show_workings)
	else:
		return None
		

def mstotime(miliseconds):
	hours, milliseconds = divmod(miliseconds, 3600000)
	minutes, milliseconds = divmod(miliseconds, 60000)
	seconds = float(milliseconds) / 1000
	s = "%i:%02i:%06.3f" % (hours, minutes, seconds)
	return s

if __name__ == '__main__':
    stepcount()
