#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

def drange(start, stop, step):
    r = start
    while r <= stop:
        yield r
        r += step

def cos(angle):
    return math.cos(math.radians(angle))

def sin(angle):
    return math.sin(math.radians(angle))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
         # Get active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
 
        # Get root component in this design
        rootComp = design.rootComponent

        # Create a new sketch on the xy plane.
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)  

        pin_radius = 0.5
        pin_circle_radius = 1.9
        number_of_pins = 13
        contraction = 0.05

        # the circumference of the rolling circle needs to be exactly equal to the pitch of the pins
        # rolling circle circumference = circumference of pin circle / number of pins
        rolling_circle_radius = pin_circle_radius / number_of_pins 
        reduction_ratio = number_of_pins + 1 # reduction ratio
        cycloid_base_radius = reduction_ratio * rolling_circle_radius # base circle diameter of cycloidal disk
        eccentricity = rolling_circle_radius - contraction

        last_point=None
        line=None

        lines=[]

        for angle in drange(0,720/reduction_ratio,0.2):
            x =  (cycloid_base_radius - rolling_circle_radius) * cos(angle)
            y =  (cycloid_base_radius - rolling_circle_radius) * sin(angle)

            point_x = x + (rolling_circle_radius - contraction) * cos(number_of_pins*-angle)
            point_y = y + (rolling_circle_radius - contraction) * sin(number_of_pins*-angle)

            if angle==0:
                # the first point
                last_point = adsk.core.Point3D.create(point_x,point_y, 0)
            else:
                line = sketch.sketchCurves.sketchLines.addByTwoPoints(
                    last_point, 
                    adsk.core.Point3D.create(point_x,point_y, 0)
                    )
                last_point=line.endSketchPoint
                lines.append(line)

            app.activeViewport.refresh()

        # Add the geometry to a collection. This uses a utility function that
        # automatically finds the connected curves and returns a collection.
        curves = sketch.findConnectedCurves(lines[0])
                
        # Create the offset.
        dirPoint = adsk.core.Point3D.create(0, 0, 0)
        offsetCurves = sketch.offset(curves, dirPoint, -pin_radius)

        # delete the original
        design.deleteEntities(curves)

       

        sketch2 = sketches.add(xyPlane)  
        # Draw the pin
        sketch2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(pin_circle_radius + eccentricity, 0, 0), pin_radius)
        # add the pin Centre of Rotation
        sketch2.sketchPoints.add(adsk.core.Point3D.create(pin_circle_radius,0,0))

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
