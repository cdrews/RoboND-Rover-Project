[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 
[nav_image]: ./output/warped_threshed.jpg
[obst_image]: ./output/warped_threshed_inv.jpg
[rock_image]: ./output/warped_threshed_rock.jpg
[video]: ./output/test_mapping.gif
[screenshot]: ./output/screenshot.png


### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

I created the color_thresh function and allowed for inverted use of it. This way I am able to create a nav map as well as a obstacle map for later use. In addition I created a rock_thresh function that finds vaguely yellow things by looking for red and green greater than 160 and blue less than 128. 
I created 3 different sets of coordinates/images from the original image. One for each rock world, navigateable world and obstacle world from the thresholding functions. I adapted them to use the Databucket use.
I re-used code developed during the quizzes to rotate and translate coordinates of the rock,nav and obstacle world into the needed coordinate frames. 
I tested all of those with various images in the notebook. Results below.

##### Thresholding/Transformation Images

| Original Image              |     |     |
| --------------------------- | --- | --- | 
| ![Calibration Rock][image3] |     |     |
| Navigation Image | Obstacle Image | Rock Image |
| ![Navigation Thresholded Image][nav_image] | ![Obstacle Image][obst_image] | ![Rock Image][rock_image] |

##### Test Mapping Video
![video][video]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

I populated the process_image function with the methods developed in the notebook. I adapted them to use the Rover class infrastructure to read sensor data and write images for debugging and diagnostic.


### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

I started out with the default `percept_step` and `decision_step` and experimented with speed, throttle and steer parameters to speed up mapping and not lose map fidelity. Adjusting the threshold parameters was also necessary to get to the best results.
I moderated the speed proportional to the mean distance of the navigatable spacein front of the rover. The throttle is then set to the difference between desired and actual speed. 

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

I used a slight 1.5 degree bias while steering in forward motion to make the robot go mostly right and thereby explore more of the terrain.
I tried to regulate the rover speed by taking into account the average open distance in front of the robot. This achieved a much higher speed, but it became necessary to filter only level images to build the map. Allowing only images that are within +/- 0.5 degree of horizontal greatly improved fidelity to >80%. 

Possible Improvements:
* when the rover is in front of a narrow obstacle it sometimes gets stuck because the average distance and angles do not see the obstacle. One improvement I would try is to use a more narrow set of the angles and distances to avoid this situation.


**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

I ran the simulator on a thinkpad T420 in 640x480 with 'good' quality setting at a frame rate of 25 frames per second. I had to use window mode. Full screen mode had my machine hang occasionally.
The framerate sometimes went as far down as 10FPS with these settings when e.g. browser windows where open at the same time.

A screenshot of a successful mapping run is below:

![alt text][screenshot]


#### Reviewer Error Message

`File "/Users/Desktop/cdrews-RoboND-Rover-Project-6c44e37/code/perception.py", line 135, in perception_step Rover.pos[0],Rover.pos[1], IndexError: index 1 is out of bounds for axis 0 with size 1`

I do not get this error message. The line that fills the Rover.pos field is
`Rover.pos = np.fromstring(data["position"], dtype=float, sep=',')` in `supporting_functions.py`. It should contain an nd.array of length 2. It could be that your version start with a None value. I added a check for None and length of Rover.pos to give better a better error if it still occurs on your system.

When I run drive_rover.py on my ubuntu 16.04 system against Roversim.x86_64 I get clean output. See below.
```
$ python drive_rover.py 
NOT recording this run ...
(11405) wsgi starting up on http://0.0.0.0:4567
(11405) accepted ('127.0.0.1', 43228)
connect  6803ff9e48e44e0e86945247edf9f75f
Current FPS: 1
dict_keys(['sample_count', 'near_sample', 'samples_x', 'brake', 'samples_y', 'pitch', 'position', 'steering_angle', 'roll', 'picking_up', 'yaw', 'speed', 'throttle', 'image', 'fixed_turn'])
speed = 0.0 position = [ 99.67   85.589] throttle = 0.0 steer_angle = 0.0 near_sample 0 picking_up 0
Current FPS: 1
dict_keys(['sample_count', 'near_sample', 'samples_x', 'brake', 'samples_y', 'pitch', 'position', 'steering_angle', 'roll', 'picking_up', 'yaw', 'speed', 'throttle', 'image', 'fixed_turn'])
speed = 0.0 position = [ 99.67   85.589] throttle = 0.0 steer_angle = 0.0 near_sample 0 picking_up 0
Current FPS: 1
```


