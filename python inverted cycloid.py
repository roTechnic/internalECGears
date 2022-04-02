import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseButton
from shapely.geometry.polygon import LinearRing
import time

blank = [[0,0]]
mm_to_inch = 1/25.4
def cos(angle):
    return np.cos(np.radians(angle))

def sin(angle):
    return np.sin(np.radians(angle))

def offset(amount, points):
    poly_line = LinearRing(points)
    poly_line_offset = poly_line.parallel_offset(amount, side="left", resolution=16, 
                                            join_style=1, mitre_limit=1)
    return poly_line_offset.coords

global clicked
def on_click(event):
    global clicked
    if event.button is MouseButton.LEFT:
        clicked=True

def setup_plot(amount):
    fig = plt.figure(figsize=(8,8))
    ax = plt.axes(xlim=(-amount,amount), ylim=(-amount,amount))
    plt.axis('off')

    plt.ion()
    plt.show()

    plt.connect('button_press_event', on_click)
    return ax

def end_plot():
    plt.ioff()
    plt.show(block=True)

def wait_for_click():
    global clicked
    clicked=False
    while clicked==False:
        plt.pause(0.1)

pin_radius = 5
pin_circle_radius = 17
number_of_pins =12

# the circumference of the rolling circle needs to be exactly equal to the pitch of the pins
# rolling circle circumference = circumference of pin circle / number of pins
rolling_circle_radius = pin_circle_radius / number_of_pins 
reduction_ratio = number_of_pins +1 # reduction ratio
cycloid_base_radius = reduction_ratio * rolling_circle_radius # base circle diameter of cycloidal disk

contraction = 0.5

eccentricity = rolling_circle_radius - contraction
print(eccentricity)

axes = setup_plot((pin_circle_radius+4*pin_radius))

cycloid_base = plt.Circle((0,0), cycloid_base_radius, fill=False, linestyle='--', lw=2)
axes.add_patch(cycloid_base)

rolling_circle = plt.Circle((0,0), rolling_circle_radius, fill=False, lw=2)
axes.add_patch(rolling_circle)

rolling_circle_line = plt.Line2D((0,1),(0,0), lw=2, color='red')
axes.add_line(rolling_circle_line)

# polygon to hold the main epicycloid
epicycloid_points = []
epicycloid = plt.Polygon(blank, fill=False, closed=False, color='red', lw=2)
axes.add_patch(epicycloid)

for angle in range(0,361):
    # rotate rolling circle round the center of the cycloid
    x =  (cycloid_base_radius - rolling_circle_radius) * cos(angle)
    y =  (cycloid_base_radius - rolling_circle_radius) * sin(angle)
    rolling_circle.center = (x, y)
    
    point_x = x + (rolling_circle_radius - contraction) * cos(number_of_pins*-angle)
    point_y = y + (rolling_circle_radius - contraction) * sin(number_of_pins*-angle)

    rolling_circle_line.set_xdata((x,point_x))
    rolling_circle_line.set_ydata((y,point_y))
    
    epicycloid_points.append([point_x,point_y])
    epicycloid.set_xy(epicycloid_points)  

    plt.pause(0.0001)

wait_for_click()
# draw pins
for pin_angle in np.linspace(0,360,num=number_of_pins+1):
    pincircle = plt.Circle(
        (pin_circle_radius*cos(pin_angle)+rolling_circle_radius - contraction,
        pin_circle_radius*sin(pin_angle))
        ,pin_radius
        )
    axes.add_patch(pincircle)
wait_for_click()

# polygon to hold the offset epicycloid
offset_epicycloid = plt.Polygon(offset(-pin_radius,epicycloid_points), fill=False, closed=False)
axes.add_patch(offset_epicycloid)

end_plot()