# Import javascript modules
from js import THREE, window, document, Object, console
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math

#-----------------------------------------------------------------------
# MAIN FUNCTION
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
    back_color = THREE.Color.new(0.1,0.1,0.1)
    scene.background = back_color
    camera = THREE.PerspectiveCamera.new(75, window.innerWidth/window.innerHeight, 0.1, 1000)
    camera.position.z = 50
    scene.add(camera)

    #create a plane to make visualization more three dimensional
    geometry = THREE.PlaneGeometry.new(2000, 2000)
    geometry.rotateX(- math.pi / 2)

    material = THREE.MeshBasicMaterial.new()
    material.transparent = True
    material.opacity = 0.5
    plane = THREE.Mesh.new(geometry, material)
    plane.position.y = -20
    plane.receiveShadow = True
    scene.add(plane)

    # Graphic Post Processing
    global composer
    post_process()

    # Set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 

    #-----------------------------------------------------------------------
    # Geometry Creation
    '''
    This is the loop I created to generate the trees.
    The idea is that max_it sets the maximum number of iterations for the
    recursive function that generates the structure. 
    Number_trees specifies how many trees should be
    built and tree_height specifies the height of the first trees. This is 
    increased in every loop iteration.'''
    max_it = 1
    number_trees = 5
    tree_height = 2
    for tree in range(0, number_trees):
        # create coordinate string
        coordinate_string = translate_coordinates(0, max_it, "gh")
        # translate the string into the coordinates for the 3d model
        g, h = use_coordinates(coordinate_string)
        # draw the tree
        my_axiom_system = system(0, tree_height, "d")
        draw_system((my_axiom_system), THREE.Vector3.new(g,-20,h))
        
        # same tree setup, but placing it in negative coordinates
        # create coordinate string with i and k to get negative value
        coordinate_string = translate_coordinates(0, max_it, "ik")
        # translate the string into the coordinates for the 3d model
        g, h = use_coordinates(coordinate_string)
        # draw the tree
        my_axiom_system = system(0, tree_height, "d")
        draw_system((my_axiom_system), THREE.Vector3.new(g,-20,h))

        # increase variables for next round of loop
        max_it = max_it + 1
        tree_height = tree_height + 1


    #-----------------------------------------------------------------------
    # USER INTERFACE
    # Set up Mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)
    
    #-----------------------------------------------------------------------
    # RENDER + UPDATE THE SCENE AND GEOMETRIES
    render()
    
#-----------------------------------------------------------------------
# HELPER FUNCTIONS
''' GENERATE_COORDINATES
define rules for coordinates for draw_system. a helper function
that is used in the recursive function translate_coordinates()
parameters: symbol: input string symbol to generate output string
returns: output string'''
def generate_coordinates(symbol):
    if symbol == "g":
        return "gg"
    elif symbol == "h":
        return "hh"
    if symbol == "i":
        return "ii"
    elif symbol == "k":
        return "kk"

'''
TRANSLATE_COORDINATES
a recursive function that creates a string of coordinates for later
tree creation.
parameters:
current_iteration: int, initially 0
max_iterations: int, defining how many recursive calls we want
axiom: string, axiom to start the string creation with
'''
def translate_coordinates(current_iteration, max_iterations, axiom):
    current_iteration += 1
    new_axiom = ""
    for symbol in axiom:
        new_axiom += generate_coordinates(symbol)
    if current_iteration >= max_iterations:
        return new_axiom
    else:
        return translate_coordinates(current_iteration, max_iterations, new_axiom)
'''
USE_COORDINATES
function that uses the previously created axiom for coordinate creation.
parameters: axiom: string
returns: start_g: int, to be used for tree placement on x-axis
start_h: int, to be used for tree placement on second axis'''
def use_coordinates(axiom):
    start_g = 0
    start_h = 0
    for symbol in axiom:
        if symbol == "g":
            start_g = start_g + 25
        if symbol == "h":
            start_h = start_h + 10
        if symbol == "i":
            start_g = start_g - 25
        if symbol == "k":
            start_h = start_h - 10
    return start_g, start_h


#-----------------------------------------------------------------------
'''
GENERATE
define the rules to be used in recursive function
params: symbol: string
returns: string or symbol (string)'''
def generate(symbol):
    if symbol == "d":
        return "abcdfbedfabedfcd"
    elif symbol == "a":
        return "aa"
    elif symbol == "b" or symbol == "c" or symbol == "e" or symbol == "f":
        return symbol
    
'''SYSTEM
A recursive function, which taken an AXIOM as an inout and runs the generate function for each symbol
'''
def system(current_iteration, max_iterations, axiom):
    current_iteration += 1
    new_axiom = ""
    for symbol in axiom:
        new_axiom += generate(symbol)
    if current_iteration >= max_iterations:
        return new_axiom
    else:
        return system(current_iteration, max_iterations, new_axiom)

'''
DRAW_SYSTEM'''
def draw_system(axiom, initial_point):
    # generate move_vec
    move_vec = THREE.Vector3.new(0,15,0)
    # empty list creation
    old_states = []
    old_move_vecs = []
    lines = []

    # for each symbol in our generated axiom, fulfill the respective task
    for symbol in axiom:
        # draws one branch of the tree
        if symbol == "a" or symbol == "d":
            start_point = THREE.Vector3.new(initial_point.x, initial_point.y, initial_point.z)
            end_point = THREE.Vector3.new(initial_point.x, initial_point.y, initial_point.z)
            end_point = end_point.add(move_vec)
            line = []
            line.append(start_point)
            line.append(end_point)
            lines.append(line)

            initial_point = end_point

        # b saves current status
        elif symbol == "b":
            old_state = THREE.Vector3.new(initial_point.x, initial_point.y, initial_point.z)
            old_move_vec = THREE.Vector3.new(move_vec.x, move_vec.y, move_vec.z)
            old_states.append(old_state)
            old_move_vecs.append(old_move_vec)

        # applies a rotation to move_vec
        elif symbol == "c": 
            move_vec.applyAxisAngle(THREE.Vector3.new(0,0,1), math.pi/7)
        # applies a rotation to move_vec
        elif symbol == "e":
            move_vec.applyAxisAngle(THREE.Vector3.new(0,0,1), -math.pi/7)
        
        # moves initial point to previous status 
        elif symbol == "f":
            initial_point = THREE.Vector3.new(old_states[-1].x, old_states[-1].y, old_states[-1].z)
            move_vec = THREE.Vector3.new(old_move_vecs[-1].x, old_move_vecs[-1].y, old_move_vecs[-1].z)
            old_states.pop(-1)
            old_move_vecs.pop(-1)
    # define global scene
    global scene
    # draw the previously generated lines to create a tree
    line_material = THREE.LineBasicMaterial.new( THREE.Color.new(0x0000ff))
    for points in lines:
        line_geom = THREE.BufferGeometry.new()
        points = to_js(points)
        console.log(points)

        line_geom.setFromPoints(points)
        vis_line = THREE.Line.new(line_geom, line_material)
        # add our tree
        scene.add(vis_line)

# Simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    #controls.update()
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

if __name__=='__main__':
    main()