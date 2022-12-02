# Import javascript modules
from js import THREE, window, document, Object
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math


#-----------------------------------------------------------------------
# MAIN PROGRAM
def main():
    #-----------------------------------------------------------------------
    # VISUAL SETUP
    # Declare the global variables
    global renderer, scene, camera, controls,composer
    
    #Set up the renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

    # Set up the scene
    scene = THREE.Scene.new()
    back_color = THREE.Color.new(0,0,0)
    scene.background = back_color
    camera = THREE.PerspectiveCamera.new(75, window.innerWidth/window.innerHeight, 0.1, 1000)
    camera.position.z = 50
    scene.add(camera)

    # Graphic Post Processing
    global composer
    post_process()

    # Set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy)

    #-----------------------------------------------------------------------
    # DESIGN / GEOMETRY GENERATION
    # Geometry Creation
    global geom_params, capsules_x, capsules_y, capsule_lines, cylinders_x, cylinders_y, cylinder_lines
    # lists for both dimensions and lines
    capsules_x = []
    capsules_y = []
    capsule_lines = []
    # second geometry: lists for both dimensions and lines
    cylinders_x = []
    cylinders_y = []
    cylinder_lines = []
    # set parameters for both geometries as dictionary
    geom_params_cylinder = {
        "radius": 5,
        "height": 20,
        "radial_segments": 32,
        "x": 2,
        "y": 2,
        "rotation_x": 45,
        "rotation_y": 0,
        "type": "cylinder"
    }
    geom_params_capsule = {
        "radius": 10,
        "length": 10,
        "capSubdivisions": 10,
        "x": 1,
        "y": 1,
        "radial_segments": 10,
        "rotation_x": 0,
        "rotation_y": 0,
        "type": "capsule"
    }
    #-----------------------------------------------------------------------
    # USER INTERACTION POSSIBLE
    # change the geometry here from capsules to cylinders as wanted
    geom_params = geom_params_cylinder
    #geom_params = geom_params_capsule
    #-----------------------------------------------------------------------
    
    geom_params = Object.fromEntries(to_js(geom_params))

    # create Materials
    global material, line_material, color, color_lines, geometry, plane, light, loader

    color = THREE.Color.new(255,255,255)
    color_lines = THREE.Color.new(255,255,255)
    material = THREE.MeshBasicMaterial.new()
    material.transparent = True
    material.opacity = 0.8
    
    geometry = THREE.PlaneGeometry.new(2000, 2000)
    geometry.rotateX(- math.pi / 2)

    # create a plane to make the simulation more grounded
    plane = THREE.Mesh.new(geometry, material)
    plane.position.y = -200
    plane.receiveShadow = True
    scene.add(plane)
    # add light
    light = THREE.PointLight.new(0xff0000, 1, 100)
    light.position.set(50, 50, 50)
    scene.add(light)

    line_material = THREE.LineBasicMaterial.new()
    line_material.color = color_lines

    
    #-----------------------------------------------------------------------
    # GEOMETRY CREATION: CAPSULE

    if geom_params.type == "capsule":
        # first for loop to create capsules on x-axis
        for i in range (geom_params.x):
            geom = THREE.CapsuleGeometry.new(geom_params.radius, geom_params.length, geom_params.capSubdivisions, geom_params.radial_segments)

            geom.translate (geom_params.radius*i*2,0,0)
            geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)

            capsule = THREE.Mesh.new(geom, material)
            capsules_x.append(capsule)
            scene.add(capsule)

            #draw the capsule lines
            edges = THREE.EdgesGeometry.new(capsule.geometry)
            line = THREE.LineSegments.new(edges,line_material)
            capsule_lines.append(line)
            scene.add(line)
            # second for loop (nested) to create capsules on second axis
            for j in range (geom_params.y):

                #after consultation with zuardin: clone the capsules 
                geom = geom.clone()

                geom.translate(0, 0, geom_params.radius*2)
                geom.rotateX(math.radians(geom_params.rotation_y)/geom_params.y*j)

                capsule = THREE.Mesh.new(geom, material)
                capsules_y.append(capsule)
                scene.add(capsule)

                # draw the capsule lines
                edges = THREE.EdgesGeometry.new(capsule.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                capsule_lines.append(line)
                scene.add(line)

    #-----------------------------------------------------------------------
    # GEOMETRY CREATION: CYLINDER
    elif geom_params.type == "cylinder":
        # first for loop to create cylinders on x axis
        for i in range (geom_params.x):
            geom = THREE.CylinderGeometry.new(geom_params.radius, geom_params.radius, geom_params.height, geom_params.radial_segments)

            geom.translate(geom_params.radius*i*2,0,0)
            geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)

            cylinder = THREE.Mesh.new(geom, material)
            cylinders_x.append(cylinder)
            scene.add(cylinder)

            #draw the cylinder lines
            edges = THREE.EdgesGeometry.new(cylinder.geometry)
            line = THREE.LineSegments.new(edges,line_material)
            cylinder_lines.append(line)
            scene.add(line)
            # inner for loop to create cylinders on second axis
            for j in range (geom_params.y):
                # clone existing geometry
                geom = geom.clone()

                geom.translate(0, 0, geom_params.radius*2)
                geom.rotateX(math.radians(geom_params.rotation_y)/geom_params.y*j)

                cylinder = THREE.Mesh.new(geom, material)
                cylinders_y.append(cylinder)
                scene.add(cylinder)

                # draw the cylinder lines
                edges = THREE.EdgesGeometry.new(cylinder.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                cylinder_lines.append(line)
                scene.add(line)


    #-----------------------------------------------------------------------

    # USER INTERFACE
    # Set up Mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)

    # Set up GUI
    gui = window.dat.GUI.new()

    param_folder = gui.addFolder('Select Geometry')

    
    param_folder = gui.addFolder('Parameters')
    # slider for changing the geometry. Adapted to the used geometries
    param_folder.add(geom_params, 'radius', 5, 100, 1)
    param_folder.add(geom_params, 'x', 1, 10, 1)
    param_folder.add(geom_params, 'y', 1, 10, 1)
    param_folder.add(geom_params, 'rotation_x', 0, 270)
    param_folder.add(geom_params, 'rotation_y', 0, 270)
    param_folder.add(geom_params, 'radial_segments',4,50)
    param_folder.open()
    
    #-----------------------------------------------------------------------
    # RENDER + UPDATE THE SCENE AND GEOMETRIES
    render()
    # end of main 

#-----------------------------------------------------------------------
# HELPER FUNCTIONS
'''
UPDATE CAPSULES: updates the capsules if the used geometry is capsule
parameters: none
returns: all wanted capsules in the scene for the webapp
'''
def update_capsules ():
    global capsules_x, capsules_y, capsule_lines, material, line_material
     
#make sure you dont have 0 capsules
    if len(capsules_x) != 0 or len(capsules_y) != 0:
        if len(capsules_x) != geom_params.x and len(capsules_y) != geom_params.y:
            # delete all capsules
            for capsule in capsules_x:
                scene.remove(capsule)
            for capsule in capsules_y:
                scene.remove(capsule)
            # delete all lines
            for line in capsule_lines: 
                scene.remove(line)

            for i in range (geom_params.x):
                # place capsules into GUI
                geom = THREE.CapsuleGeometry.new(geom_params.radius, geom_params.length, geom_params.capSubdivisions, geom_params.radial_segments)
                geom.translate (geom_params.radius*2*i,0,0)
                geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)
                # create capsules
                capsule = THREE.Mesh.new(geom, material)
                capsules_x.append(capsule)
                scene.add(capsule)

                #draw the capsule lines
                edges = THREE.EdgesGeometry.new(capsule.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                capsule_lines.append(line)
                # place capsules in scene
                scene.add(line)
                for j in range(geom_params.y):
                    geom = geom.clone()

                    geom.translate(0, 0, geom_params.radius * 2)
                    geom.rotateX(math.radians(geom_params.rotation_y) / geom_params.y * j)

                    capsule = THREE.Mesh.new(geom, material)
                    capsules_y.append(capsule)
                    scene.add(capsule)

                    # draw the capsule lines
                    edges = THREE.EdgesGeometry.new(capsule.geometry)
                    line = THREE.LineSegments.new(edges, line_material)
                    capsule_lines.append(line)
                    scene.add(line)
        else:
            for i in range (len(capsules_x)):
                capsule = capsules_x[i]
                line = capsule_lines[i]
                # place the capsule in GUI, are already there but are placedin a new way in x directon 
                geom = THREE.CapsuleGeometry.new(geom_params.radius, geom_params.length, geom_params.capSubdivisions, geom_params.radial_segments)
                geom.translate (geom_params.radius*2,0,0)
                geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)
    
                capsule.geometry = geom
    
                edges = THREE.EdgesGeometry.new(capsule.geometry)
                line.geometry = edges
                for j in range(len(capsules_y)):
                    capsule = capsules_y[j]
                    line = capsule_lines[len(capsules_x)+j]
                    # place the capsule in GUI, are already there but are placedin a new way in y directon
                    geom = THREE.CapsuleGeometry.new(geom_params.radius, geom_params.length, geom_params.capSubdivisions, geom_params.radial_segments)
                    geom.translate(0,0, geom_params.radius * 2)
                    geom.rotateX(math.radians(geom_params.rotation_y) / geom_params.y * j)

                    capsule.geometry = geom

                    edges = THREE.EdgesGeometry.new(capsule.geometry)
                    line.geometry = edges


#-----------------------------------------------------------------------           



'''UPDATE CYLINDERS: updates the cylinders if the used geometry is cylinder
parameters: none
returns: all wanted cylinders in the scene for the webapp
'''
def update_cylinders():
    global cylinders_x, cylinders_y, cylinder_lines, material, line_material

    # make sure you dont have 0 cylinders total
    if len(cylinders_x) != 0 or len(cylinders_y) != 0:
        if len(cylinders_x) != geom_params.x and len(cylinders_y) != geom_params.y:
            # delete all cylinders 
            for cylinder in cylinders_x:
                scene.remove(cylinder)
            for cylinder in cylinders_y:
                scene.remove(cylinder)
            # delete all lines 
            for line in cylinder_lines: 
                scene.remove(line)
            
            # place new cylinders. Same structure as used above, using a nested for loop
            for i in range (geom_params.x):
                # create and place the cylinder in GUI
                geom = THREE.CylinderGeometry.new(geom_params.radius, geom_params.radius, geom_params.height, geom_params.radial_segments)
                geom.translate (geom_params.radius*i*2,0,0)
                geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)
                
                cylinder = THREE.Mesh.new(geom, material)
                cylinders_x.append(cylinder)
                scene.add(cylinder)

                #draw the cylinder lines
                edges = THREE.EdgesGeometry.new(cylinder.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                cylinder_lines.append(line)
                # place cylinder in scene 
                scene.add(line)
                # inner for loop
                for j in range(geom_params.y):
                    geom = geom.clone()
                    geom.translate(0, 0, geom_params.radius * 2)
                    geom.rotateX(math.radians(geom_params.rotation_y) / geom_params.x * j)

                    cylinder = THREE.Mesh.new(geom, material)
                    cylinders_y.append(cylinder)
                    scene.add(cylinder)

                    # draw the cylinder lines
                    edges = THREE.EdgesGeometry.new(cylinder.geometry)
                    line = THREE.LineSegments.new(edges, line_material)
                    cylinder_lines.append(line)
                    scene.add(line)
        else:
            for i in range (len(cylinders_x)):
                cylinder = cylinders_x[i]
                line = cylinder_lines[i]
                # place the capsule in GUI, are already there but are placedin a new way in x directon
                geom = THREE.CylinderGeometry.new(geom_params.radius, geom_params.radius, geom_params.height, geom_params.radial_segments)
                geom.translate (geom_params.radius*i*2,0,0)
                geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)
    
                cylinder.geometry = geom
    
                edges = THREE.EdgesGeometry.new(cylinder.geometry)
                line.geometry = edges
                for j in range(len(cylinders_y)):
                    cylinder = cylinders_y[j]
                    line = cylinder_lines[len(cylinders_x)+j]
                    # place the capsule in GUI, are already there but are placedin a new way in y directon
                    geom = THREE.CylinderGeometry.new(geom_params.radius, geom_params.radius,
                                                    geom_params.height, geom_params.radial_segments)
                    geom.translate(0,0, geom_params.radius * 2)
                    geom.rotateX(math.radians(geom_params.rotation_y) / geom_params.y * j)

                    cylinder.geometry = geom

                    edges = THREE.EdgesGeometry.new(cylinder.geometry)
                    line.geometry = edges
                



# Simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    update_cylinders()
    update_capsules()
    controls.update()
    composer.render()

# Graphical post-processing
def post_process():
    render_pass = THREE.RenderPass.new(scene, camera)
    render_pass.clearColor = THREE.Color.new(0,0,0)
    render_pass.ClearAlpha = 0
    fxaa_pass = THREE.ShaderPass.new(THREE.FXAAShader)

    pixelRatio = window.devicePixelRatio

    fxaa_pass.material.uniforms.resolution.value.x = 1 / ( window.innerWidth * pixelRatio )
    fxaa_pass.material.uniforms.resolution.value.y = 1 / ( window.innerHeight * pixelRatio )
   
    global composer
    composer = THREE.EffectComposer.new(renderer)
    composer.addPass(render_pass)
    composer.addPass(fxaa_pass)

# Adjust display when window size changes
def on_window_resize(event):

    event.preventDefault()

    global renderer
    global camera
    
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize( window.innerWidth, window.innerHeight )

    #post processing after resize
    post_process()
#-----------------------------------------------------------------------
#RUN THE MAIN PROGRAM
if __name__=='__main__':
    main()
    