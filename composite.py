# Written for Python 3.6.9
# Install required packages (numpy and opencv) with pip:
#     pip3 install opencv-python
#     pip3 install numpy
# Usage: python3 composite.py [options] <input_file>
# Options:
#     -h                Print this message, then exit
#     -o <output_file>  Composites will be written to this path (default: out.png)
#     -f                Full-scale composites will be generated
#     -w <width>        Composites will default to this width, in frames
#     -a                Automatically generate a composite, no gui
# Controls:
#     A, D              Decrease/increase composite width
#     W, S              Increase/decrease step size
#     Q                 Print current width and step size
#     Enter             Export composite to output file (set by -o)

import sys
import math
import numpy as np
import cv2

# Convert a video stream to an aggregate image (composite with height=1)
def read_agg_image(capture, full_scale=False):
  frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
  if full_scale:
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    agg_image = np.zeros(shape=(frame_height, frame_width*frame_count, 3))
  else:
    agg_image = np.zeros(shape=(1, frame_count, 3))
  success, image = capture.read()
  count = 0
  while success:
    if full_scale:
      agg_image[0:frame_height, frame_width*count:frame_width*(count+1)] = image
    else:
      mini_image = cv2.resize(image, (1, 1))
      agg_image[0, count] = mini_image
    success, image = capture.read()
    count += 1
  return agg_image

# Resize an image to given width, using compositing rules
def pad_resize(image, width, frame_width=1, frame_height=1):
  frame_count = ((image.size // frame_width) // frame_height) // 3
  height = math.ceil(frame_count / width)
  ret_image = np.zeros(shape=(height * frame_height, math.ceil(width) * frame_width, 3))
  x = 0
  y = 0
  accumulator = 0
  for i in range(frame_count):
    y_offset = y*frame_height
    x_offset = x*frame_width
    ret_image[y*frame_height:(y+1)*frame_height, x*frame_width:(x+1)*frame_width] = \
        image[0:frame_height, i*frame_width:(i+1)*frame_width]
    accumulator += 1
    x += 1
    if accumulator >= width:
      accumulator -= width
      x = 0
      y += 1
  return ret_image

def main():
  # Initialize arguments to be parsed from command line
  in_file = None
  out_file = 'out.png'
  full_scale = False
  final_width = -1
  no_gui = False
  usage_message = ('Usage: python3 composite.py [options] <input_file>\n'
                   'Options:\n'
                   '    -h                Print this message, then exit\n'
                   '    -o <output_file>  Composites will be written to this path (default: out.png)\n'
                   '    -f                Full-scale composites will be generated\n'
                   '    -w <width>        Composites will default to this width, in frames\n'
                   '    -a                Automatically generate a composite, no gui\n'
                   'Controls:\n'
                   '    A, D              Decrease/increase composite width\n'
                   '    W, S              Increase/decrease step size\n'
                   '    Q                 Print current width and step size\n'
                   '    Enter             Export composite to output file (set by -o)')

  # Parse command line arguments  
  i = 1
  while i < len(sys.argv):
    if sys.argv[i] == '-h':
      print(usage_message)
      return    # Exit prematurely
    elif sys.argv[i] == '-o':
      i += 1
      if i >= len(sys.argv) or sys.argv[i].startswith('-'):
        print('ERROR: Must specify a file name after -o')
        return    # Exit prematurely
      else:
        out_file = sys.argv[i]
    elif sys.argv[i] == '-f':
      full_scale = True
    elif sys.argv[i] == '-w':
      i += 1
      if i >= len(sys.argv):
        print('ERROR: Must specify a number after -w')
        return    # Exit prematurely
      else:
        try:
          final_width = int(sys.argv[i])
        except ValueError:
          try:
            final_width = float(sys.argv[i])
          except ValueError:
            print('ERROR: Must specify a number after -w')
            return    # Exit prematurely
        if final_width <= 0:
          print('ERROR: Width must be greater than 0')
          return    # Exit prematurely
    elif sys.argv[i] == '-a':
      no_gui = True
    elif sys.argv[i].startswith('-') and len(sys.argv[i]) == 2:
      print('ERROR: Unrecognized option:', sys.argv[i])
      return    # Exit prematurely
    else:
      if in_file is None:
        in_file = sys.argv[i]
      else:
        print('ERROR: Unknown token or duplicate file name:', sys.argv[i])
        return    # Exit prematurely
    i += 1

  # Check command line arguments for validity
  if in_file is None:
    if len(sys.argv) == 1:
      print(usage_message)
      return    # Exit prematurely
    else:
      print('ERROR: Must specify an input file name')
      return    # Exit prematurely
  # TODO: Display warning when out_file already exists (y/n)?
  if full_scale and (in_file.endswith('.png') or in_file.endswith('jpg')):
    print('ERROR: Full scale mode not available when input file is an image')
    return    # Exit prematurely
  if no_gui and final_width <= 0:
    print('WARNING: Auto mode enabled with no specified width (square will be used)')

  # Check if input file exists
  try:
    open(in_file)
  except FileNotFoundError:
    print('ERROR: Input file not found:', in_file)
    return    # Exit prematurely

  # Generate aggregate image (composite with height=1) from input file
  agg_image = None
  frame_width = 1
  frame_height = 1
  if in_file.lower().endswith('.png') or in_file.lower().endswith('.jpg') or in_file.lower().endswith('.jpeg'):
    read_image = cv2.imread(in_file, cv2.IMREAD_COLOR)
    if read_image is None:
      print('ERROR: Couldn\'t open image:', in_file)
      return    # Exit prematurely
    width, height, channels = read_image.shape
    agg_image = read_image.reshape(1, width * height, channels)
    print('Read %d frames from %s' % (agg_image.shape[1], in_file))
  else:
    capture = cv2.VideoCapture(in_file)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if frame_count == 0:
      print('ERROR: Couldn\'t open video:', in_file)
      return    # Exit prematurely
    if full_scale:
      print('Reading %d frames at %dx%d from %s...' %
          (frame_count, frame_width, frame_height, in_file), end='', flush=True)
    else:
      print('Reading %d frames from %s...' % (frame_count, in_file), end='', flush=True)
    agg_image = read_agg_image(capture, full_scale)
    print('SUCCESS')
  if not full_scale:
    frame_width = 1
    frame_height = 1

  # Calculate a good starting width (if not already specified by user)
  if final_width <= 0:
    final_width = int(math.ceil(math.sqrt(agg_image.shape[1])))

  # If auto mode is enabled, make one composite and exit
  if no_gui:
    final_image = pad_resize(agg_image, final_width, frame_width, frame_height)
    cv2.imwrite(out_file, final_image)
    print('Image saved to', out_file)
    return

  # Enter gui mode
  cv2.namedWindow('Composite Image', cv2.WINDOW_NORMAL)
  redraw = True
  step_size = 1
  while True:
    if redraw:
      final_image = pad_resize(agg_image, final_width, frame_width, frame_height)
      cv2.imshow('Composite Image', final_image / 255)
      redraw = False
    key = cv2.waitKey(100)
    if key == ord('w') or key == 82:
      step_size = 10*step_size
    elif key == ord('s') or key == 84:
      step_size = step_size / 10
    if key == ord('a') or key == 81:
      final_width -= step_size
      if final_width < 1:
        final_width = 1
      redraw = True
    elif key == ord('d') or key == 83:
      final_width += step_size
      if final_width > agg_image.shape[1]:
        final_width = agg_image.shape[1]
      redraw = True
    elif key == ord('q') or key == 83:
      print('width=%r, step_size=%r' % (final_width, step_size))
    elif key == 13:
      cv2.imwrite(out_file, final_image)
      print('Image saved to', out_file)
    elif key == 27:
      cv2.destroyAllWindows()
      return
    elif key == -1 and cv2.getWindowProperty('Composite Image', cv2.WND_PROP_VISIBLE) < 1:
      return
      

if __name__ == '__main__':
  main()
