import argparse
import cv2
import imutils
import numpy as np
import requests
import re
import enchant
from imutils import contours
from PIL import Image
import pytesseract
import os

def perform_ocr_on_card(image_path):
	API_ENDPOINT = "https://api.ocr.space/parse/image"
	API_KEY = "d33078b0b988957"

	data = {
		'apikey': API_KEY,
		'isOverlayRequired': True,
	}

	with open(image_path, 'rb') as file:
		# print(file.read())
		response = requests.post(url=API_ENDPOINT, files={image_path: file}, data=data)
		return response.json()['ParsedResults'][0]['TextOverlay']['Lines']

def sort_contours(cnts, method="lr"):
	# Initialize the reverse flag and sort index
	reverse = False
	index = 0

	# Handle if we need to sort in reverse
	if method == 'rl' or method == 'bt':
		reverse = True

	# Handle if we are sorting against the y-coordinate rather than the x-coordinate
	# of the bounding box
	if method == 'tb' or method == 'bt':
		index = 1

	# Construct the list of bounding boxes and sort them from top to bottom
	boundingBoxes = [cv2.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][index], reverse=reverse))

	# Return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)

def get_words_from_grid(image_path):
	print('in get words')
	print(image_path)
	# Create the arg parser
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-i", "--image", required = True, help = "Path to the image")
	# args = vars(ap.parse_args())

	# Set the image to be from the path that was passed in
	image = cv2.imread(image_path)
	image = imutils.rotate(image, 180)
	cv2.waitKey(0)

	# Resize the image
	image = imutils.resize(image, width=1500)
	colored = image.copy()

	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	cv2.imwrite('images/cn-r.jpg', image)

	edged = cv2.Canny(image, 30, 150)

	# Find the contours
	print('finding contours')
	(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	sorted_cnts = sorted(cnts, key = cv2.contourArea, reverse=True)[:25]
	(sorted_cnts_by_lr, bounding_boxes_lr) = sort_contours(sorted_cnts, method='lr')



	# word_set = image.copy()

	cnts_sorted_by_y_coord = []
	for idx in range(0, 5):
		(cnts, _) = zip(*sorted(zip(sorted_cnts_by_lr[idx * 5:idx * 5 + 5], bounding_boxes_lr[idx * 5:idx * 5 + 5]), key=lambda b: b[1][1], reverse=False))	
		cnts_sorted_by_y_coord.extend(cnts)

	# print(get_word_from_contour(colored.copy(), cnts_sorted_by_y_coord[0]))

	word_grid_map = []
	for idx in range(0, 5):
		current_column = map(lambda x: get_word_from_contour(colored.copy(), x), cnts_sorted_by_y_coord[idx * 5:idx * 5 + 5])
		word_grid_map.append(list(current_column))

	print(word_grid_map)

	# mask = np.zeros(colored.shape[:2], dtype="uint8")
	# cv2.drawContours(mask, [sorted_cnts[0]], -1, 255, -1)
	# out = np.zeros_like(image)
	# out[mask == 255] = image[mask == 255]
	# cv2.imwrite('test.jpg', out)
	# text = pytesseract.image_to_string(Image.open('test.jpg'))
	# os.remove('test.jpg')
	# print(text.split('\n'))

	# ocr_results = perform_ocr_on_card('images/cn-r.jpg')
	# text = pytesseract.image_to_string(Image.open('images/cn-r.jpg'))

	# parsed_results = []

	# dictionary = enchant.Dict('en_US')
	# for result in text.split('\n'):
	# 	has_num = re.search('\d+', result)
	# 	all_uppercase = result == result.upper()
	# 	if result != '' and dictionary.check(result) and not has_num and all_uppercase:
	# 		parsed_results.append(result)

	# print(parsed_results)
	# for result in ocr_results:
	# 	for word in result['Words']:
	# 		has_num = re.search('\d+', word['WordText'])
	# 		all_uppercase = word['WordText'] == word['WordText'].upper()
	# 		if dictionary.check(word['WordText']) and not has_num and all_uppercase:
	# 			parsed_results.append(word)

	# # Make the words into a 5x5 grid
	# words_as_grid = []
	# current_column = []

	# for idx in range(0, 5):
	# 	current_column = map(lambda x: x['WordText'], parsed_results[idx * 5:idx * 5 + 5])
	# 	words_as_grid.append(list(current_column))

	# return words_as_grid
	cv2.waitKey(0)

def get_word_from_contour(image, cnt):
	# Create a mask of image with all 0's
	mask = np.zeros(image.shape[:2], dtype="uint8")
	# Draw the contour onto the mask
	cv2.drawContours(mask, [cnt], -1, 255, -1)

	out = np.zeros_like(image)
	out[mask == 255] = image[mask == 255]
	out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(out, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	# gray = cv2.medianBlur(out, 3)

	(x, y) = np.where(mask == 255)
	(topx, topy) = (np.min(x), np.min(y))
	(bottomx, bottomy) = (np.max(x), np.max(y))
	cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

	cv2.imwrite('test.jpg', cropped)
	text = pytesseract.image_to_string(Image.open('test.jpg'))
	os.remove('test.jpg')

	found_word = ''
	print(text)
	dictionary = enchant.Dict('en_US')
	for result in text.split('\n'):
		has_num = re.search('\d+', result)
		all_uppercase = result == result.upper()
		if result != '' and dictionary.check(result) and not has_num and all_uppercase:
			found_word = result

	return found_word

if __name__ == '__main__':
	get_words_from_grid('')