import numpy as np
import cv2


def color_thresh(img, rgb_thresh=(120, 120, 150),inv=False):
    # Create an array of zeros same xy size as img, but single channel
    if inv:
        color_select = np.ones_like((img[:,:,0]>0))
    else:
        color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    if inv:
        color_select[above_thresh] = 0
    else:
        color_select[above_thresh] = 1
        
    # Return the binary image
    return color_select

def rock_thresh(img, rgb_thresh=(160, 160, 128)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select


# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # yaw angle is recorded in degrees so first convert to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = xpix * np.cos(yaw_rad) - ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    xpix_translated = np.int_(xpos + (xpix_rot / scale))
    ypix_translated = np.int_(ypos + (ypix_rot / scale))
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

#figure out if rover is level enough to use the picture for mapping
def is_level(Rover):
    return ( Rover.roll > 359.5 or Rover.roll < 0.5 ) and ( Rover.pitch > 359.5 or Rover.pitch < 0.5 )

# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                  [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                  ])
    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples 
    nav_img   = color_thresh(warped,(120,120,150))
    rock_img  = rock_thresh(warped,(160,160,128))
    obst_img  = color_thresh(warped,(120,120,150),inv=True)
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    #Rover.vision_image = warped
    Rover.vision_image[:,:,0] = obst_img * 200
    Rover.vision_image[:,:,1] = rock_img * 200 
    Rover.vision_image[:,:,2] = nav_img * 200

    # 5) Convert map image pixel values to rover-centric coords
    x_pix_nav,y_pix_nav   = rover_coords(nav_img)
    x_pix_rock,y_pix_rock = rover_coords(rock_img)
    x_pix_obst,y_pix_obst = rover_coords(obst_img)

    # 6) Convert rover-centric pixel values to world coordinates
    # pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    if Rover.pos is None or len(Rover.pos) != 2:
        print("Rover.pos does not contain a nd.array of 2 elements, but contains [%s] instead"%(Rover.pos))
        return Rover
    x_pix_world_nav,y_pix_world_nav = pix_to_world(x_pix_nav,y_pix_nav,
                                           Rover.pos[0],Rover.pos[1],
                                           Rover.yaw,
                                           Rover.worldmap.shape[0],10)
    x_pix_world_rock,y_pix_world_rock = pix_to_world(x_pix_rock,y_pix_rock,
                                           Rover.pos[0],Rover.pos[1],
                                           Rover.yaw,
                                           Rover.worldmap.shape[0],10)
    x_pix_world_obst,y_pix_world_obst = pix_to_world(x_pix_obst,y_pix_obst,
                                           Rover.pos[0],Rover.pos[1],
                                           Rover.yaw,
                                           Rover.worldmap.shape[0],10)
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    if is_level(Rover):
        Rover.worldmap[y_pix_world_obst, x_pix_world_obst, 0] += 2
        Rover.worldmap[y_pix_world_rock, x_pix_world_rock, 1] += 2
        Rover.worldmap[y_pix_world_nav , x_pix_world_nav , 2] += 2

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    Rover.nav_dist, Rover.nav_angles = to_polar_coords(x_pix_nav, y_pix_nav)
    
    return Rover
