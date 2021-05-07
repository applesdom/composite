# composite.py
Small GUI for generating composite images

![BRINE width=540.7](https://github.com/applesdom/composite/blob/main/samples/BRINE_540_7.png)

### Installation

Written for Python 3.6.9. Use pip to install required packages:

    pip3 install opencv-python  
    pip3 install numpy

### Getting Started

Composite images are formed by down-scaling each frame of a target video into a
single pixel. Feed this script a video file (.mp4, .mkv, or .webm) and use the
GUI to tune the shape of the output image. Or feed the script an existing
composite to perform reshaping. Full-scale composites which use the entire video
frame can also be generated.

    Usage: python3 composite.py [options] <input_file>  
    Options:  
        -h                Print this message, then exit  
        -o <output_file>  Composites will be written to this path (default: out.png)  
        -f                Full-scale composites will be generated  
        -w <width>        Composites will default to this width, in frames  
        -a                Automatically generate a composite, no gui  
        -r <start>:<end>  Only use pixels in this index range (including start)
    Controls:  
        A, D              Decrease/increase composite width  
        W, S              Increase/decrease step size  
        Q                 Print current width and step size  
        Enter             Export composite to output file (set by -o)`
        
### Examples

    python3 composite.py N_BRILL.mp4                  # Open GUI with "N_BRILL.mp4" as input
    python3 composite.py com.png -o new.png           # Open GUI with "com.png" as input, write reshaped images to "new.png"
    python3 composite.py LOCK.mkv -a -f -w 197.36     # Automatically generate a full-scale composite for "LOCK.mkv" using
                                                      # width=197.36 (GUI will not be shown)
