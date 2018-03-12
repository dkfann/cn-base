import argparse
import cv2
import imutils
import numpy as np
from functools import reduce

def determine_color_of_cell(color_masks, image, contour):
	# Create the mask of the contour in the image
	mask = np.zeros(image.shape[:2], dtype="uint8")
	cv2.drawContours(mask, [contour], -1, 255, -1)

	color_values_per_channel = []

	for idx in range(0, len(color_masks)):
		contour_with_color = cv2.bitwise_and(color_masks[idx].copy(), color_masks[idx].copy(), mask = mask)
		(T, threshold)  = cv2.threshold(contour_with_color, 20, 255, cv2.THRESH_BINARY)

		nonzeros = np.nonzero(threshold)
		num_of_active_pixels_across_channels = len(reduce(lambda x, y: x + y, [channel for channel in nonzeros]))
		color_values_per_channel.append(num_of_active_pixels_across_channels)

	selected_idx = None

	for idx in range(0, len(color_values_per_channel)):
		if color_values_per_channel[idx] > 1000:
			selected_idx = idx

	if selected_idx == None:
		selected_idx = 3

	return selected_idx

def generate_color_masks_for_image(image):
	# Color mask order: Red, Blue, Brown
	color_boundaries = [
		([17, 15, 100], [50, 56, 200]),
		([56, 20, 2], [220, 88, 50]),
		([57, 84, 99], [91, 156, 191]),
	]

	color_masks = []

	for (lower, upper) in color_boundaries:
		lower = np.array(lower, dtype="uint8")
		upper = np.array(upper, dtype="uint8")

		# Find the colors within the specified boundaries and apply the mask
		mask = cv2.inRange(image, lower, upper)
		output = cv2.bitwise_and(image, image, mask = mask)
		color_masks.append(output)

	return color_masks

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

def get_spymaster_cells(image_path):
	# Create the arg parser
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-i", "--image", required = True, help = "Path to the image")
	# args = vars(ap.parse_args())

	# Set the image to be from the path that was passed in
	image = cv2.imread(image_path)

	# Resize the image
	image = imutils.resize(image, width=700)

	# Convert to Gray and Thresholding
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Perform the Canny Edge detection with no blurring
	edged = cv2.Canny(gray, 30, 150)

	# Find the contours
	(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	sorted_cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:25]
	(sorted_cnts_by_lr, bounding_boxes_lr) = sort_contours(sorted_cnts, method='lr')

	cells = image.copy()
	cnts_sorted_by_y_coord = []
	for idx in range(0, 5):
		(cnts, _) = zip(*sorted(zip(sorted_cnts_by_lr[idx * 5:idx * 5 + 5], bounding_boxes_lr[idx * 5:idx * 5 + 5]), key=lambda b: b[1][1], reverse=False))	
		cnts_sorted_by_y_coord.extend(cnts)

	color_masks = generate_color_masks_for_image(image)
	color_grid_map = []

	for idx in range(0, 5):
		current_column = map(lambda x: determine_color_of_cell(color_masks, image, x), cnts_sorted_by_y_coord[idx * 5:idx * 5 + 5])
		color_grid_map.append(list(current_column))

	return color_grid_map

if __name__ == '__main__':
	get_spymaster_cells('')