#!/usr/bin/env python3

import glob
import numpy as np

BACKSTR = '\t\t\t"string background" ["../textures/background2.exr"]\r\n'

def gaussian(x, mu, sig):
    return min([1.5, float(np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.))) * 2.5)])

def curve(x, a, b, c):
    return max([-c*(x-b)**2+a, 0.0])

c = 0.01
a = 2
b = 35/2
mu = b
sig = 7

kf = 0
for scene_file in glob.glob('[0-9][0-9][0-9][0-9]/myScene1.[0-9][0-9][0-9][0-9].pbrt'):
	frame_number = int(scene_file[0:4])
	with open(scene_file, 'r') as scene:
		lines = scene.readlines()

		lines[12] = 'VolumeIntegrator "single" "float stepsize" [.05]\n'

		# lines[1] = '\t"integer xresolution" [1080]\n'
		# lines[2] = '\t"integer yresolution" [720]\n'
		# lines[37] = '\t"string filename"["../textures/background2.exr"]\n'

		# if lines[93] == '\tAttributeEnd\r\n':
		# 	print('[frame %04d]\tPatching infinite light background' % frame_number)
		# 	lines.insert(93, BACKSTR)
		# else:
		# 	lines[93] = BACKSTR

		deleting = False
		for l in range(139, len(lines)):
			line = lines[l]
			if 'AttributeBegin' in line:
				print('[frame %04d]\tRemoving old vortex' % frame_number)
				deleting = True
			if deleting:
				lines[l] = ''
			if 'AttributeEnd' in line:
				deleting = False

		p = gaussian(kf, mu, sig)
		p = max([gaussian(kf, mu, sig), curve(kf, a, b, c)])
		print('[frame %04d]\tInserting vortex' % frame_number)
		lines.insert(143,
"""	AttributeBegin
		ConcatTransform [0.413438 -0.012901 -0.024256 0.000000
	                 0.018106 -0.147198 0.386899 0.000000
	                 -0.020664 -0.387107 -0.146310 0.000000
	                 -4.989242 -8.175680 2.754618 1.000000]
        Scale 10 10 10
		Translate 0 0 0.3
		Rotate {rotation} 0 1 0
		Volume "vortex"
		"point p0" [-1 -1 -1] "point p1" [ 1 2 1 ]
		"color sigma_a" [1 1 2]
		"color sigma_s" [6 6 4]
		"color Le" [1 1 10]
		"float killbelow" [-0.5]
		"float step" [{step}]
		"float p" [{p}]
	AttributeEnd
""".format(
		rotation=kf*-4,
		step=kf * 0.05,
		p=p
	))
		print(p)

	kf += 1
	with open(scene_file, 'w') as scene:
		scene.write(''.join(lines))
