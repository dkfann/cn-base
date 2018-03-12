import argparse
import spy_words
import spy_cells
import cv2

def generate_words_and_color_map():
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-w", "--words", required = True, help = "Path to words image")
	# ap.add_argument("-c", "--cells", required = True, help = "Path to spymaster cells")
	# args = vars(ap.parse_args())

	# words_image_path = args["words"]
	# cells_image_path = args["cells"]
	words_image_path = 'images/cn-full.jpg'
	cells_image_path = 'images/cells.jpg'

	words_in_grid = spy_words.get_words_from_grid(words_image_path)
	# colors_in_grid = spy_cells.get_spymaster_cells(cells_image_path)

	# words_and_color_map = []
	# for idx in range(0, len(words_in_grid)):
	# 	mapping_column = zip(words_in_grid[idx], colors_in_grid[idx])
	# 	words_and_color_map.append(list(mapping_column))

	# print(words_and_color_map)

def test():
	print('in spy map')

if __name__ == '__main__':
	generate_words_and_color_map()