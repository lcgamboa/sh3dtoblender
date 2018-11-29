#  ########################################################################
#
#   SweetHome3D XML to Blender inporter
#
#  ########################################################################
#
#   Copyright (c) : 2018  Luis Claudio Gambôa Lopes
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#   For e-mail suggestions :  lcgamboa@yahoo.com
#  ######################################################################## */

# How to use:
#   1-Open Sweethome 3D  http://www.sweethome3d.com
#   2-Create or open a existent house
#   3-Use the plugin EXPORT to XML http://www.sweethome3d.com/support/forum/viewthread_thread,6708
#   4-Open blender 
#   5-Choose Text Editor window and open sh3d_xml_to_blender.py script
#   6-Run the script, in the File dialog choose the zip file generate by SweetHome 3D EXPORT to HTML5 plugin
   
# It's possible use the imported model with blender render and blender engine (the script add Logic blocks for FPS game like behavior)
# To render with blender cycles it's necessary inport the materials. Try use https://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Material/Blender_Cycles_Materials_Converter

from zipfile import ZipFile
from xml.etree import cElementTree as ElementTree
from collections import namedtuple
from urllib.parse import unquote
    
import os
import math
import bpy
import mathutils
import struct
import shutil

scale=0.05
speed=0.5

class OpenFile(bpy.types.Operator):
  bl_idname = "object.openfile"
  bl_label = "Open"
  filename_ext = ".zip"
  filter_glob = bpy.props.StringProperty(default='*.zip', options={'HIDDEN'}, maxlen=255)

 
  filepath = bpy.props.StringProperty(subtype="FILE_PATH")

  def execute(self, context):
      
    zip_name=self.filepath


    #file paths ans zip extraction dirs

    zip_path = os.path.abspath(zip_name)
    zip_dir = os.path.dirname(zip_path)
    xml_path=os.path.join(zip_dir, 'xml')

    #remove old files
    shutil.rmtree(xml_path,True)
    
    #unzip files
    with ZipFile(zip_path, 'r') as zip_file:
       zip_file.extractall(xml_path)


    #clear scene
    bpy.data.scenes["Scene"].unit_settings.scale_length=1.0
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    #clear images
    imgs = bpy.data.images
    for image in imgs:
        image.user_clear()

    #clear materials
    for material in bpy.data.materials:
        material.user_clear();
        bpy.data.materials.remove(material)    
        
    #clear textures
    textures = bpy.data.textures
    for tex in textures:
        tex.user_clear()
        bpy.data.textures.remove(tex)


    #read xml and files
    xmlPath = os.path.join(xml_path,'Home.xml')
    xmlRoot = ElementTree.parse(xmlPath).getroot()

    #read house
    filename=os.path.join(xml_path,xmlRoot.get('structure'))
    bpy.ops.import_scene.obj(filepath=filename)
    obs = bpy.context.selected_editable_objects[:] 
    bpy.context.scene.objects.active=obs[0]
    bpy.ops.object.join()
    obs[0].name=xmlRoot.get('name')
    obs[0].dimensions=obs[0].dimensions*scale
    obs[0].location=(0.0, 0.0, 0.0)
    bpy.ops.object.shade_flat()
    bpy.context.active_object.layers[0]= True
    bpy.context.active_object.layers[1]= False
    bpy.context.active_object.layers[2]= False
    bpy.context.active_object.layers[3]= False

    Level = namedtuple("Level", "id elev ft")
    levels=[]

    for element in xmlRoot:
      objectName = element.tag

      if objectName == 'level':
         levels.append(Level(id=element.get('id'),elev=float(element.get('elevation')),ft=float(element.get('floorThickness'))))
           
      if objectName == 'furnitureGroup':       
         for furniture in element:
            xmlRoot.append(furniture);      
      
      #if objectName in ('doorOrWindow','pieceOfFurniture'):
      if 'model' in element.keys():  
        print(objectName)   
        filename=os.path.join(xml_path,unquote(element.get('model')))
        dimX = float(element.get('width'))
        dimY = float(element.get('height'))
        dimZ = float(element.get('depth')) 
        
        locX = float(element.get('x'))*scale
        locY = -float(element.get('y'))*scale
        
        lve=0.0;
        if 'level' in element.keys():
          for lv in levels:
            if lv.id == element.get('level'):
              lve=(lv.elev)*scale
               
           
        if 'elevation' in element.keys():
          locZ= (dimY*scale/2.0)+(float(element.get('elevation'))*scale)+lve 
        else:    
          locZ= (dimY*scale/2.0)+lve  

        
        bpy.ops.import_scene.obj(filepath=filename)
        obs = bpy.context.selected_editable_objects[:] 
        bpy.context.scene.objects.active=obs[0]
        bpy.ops.object.join()
        obs[0].name=element.get('name')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')     
        if objectName in ('doorOrWindow'):   
           bpy.context.active_object.layers[1]= True  
           bpy.context.active_object.layers[2]= False        
        else:
           bpy.context.active_object.layers[2]= True
           bpy.context.active_object.layers[1]= False
        bpy.context.active_object.layers[0]= False
        bpy.context.active_object.layers[3]= False
        
        if 'modelMirrored' in element.keys():
          if element.get('modelMirrored') == 'true':
            bpy.ops.transform.mirror(constraint_axis=(True, False, False),constraint_orientation='GLOBAL', proportional='DISABLED')
      
        if 'modelRotation' in element.keys():
          value=element.get('modelRotation')
          va=value.split()
          
          mat_rot = mathutils.Matrix()

          mat_rot[0][0]=float(va[0])
          mat_rot[0][1]=float(va[1])
          mat_rot[0][2]=float(va[2])
          mat_rot[1][0]=float(va[3])
          mat_rot[1][1]=float(va[4])
          mat_rot[1][2]=float(va[5])
          mat_rot[2][0]=float(va[6])
          mat_rot[2][1]=float(va[7])
          mat_rot[2][2]=float(va[8])

          ob = bpy.context.object   
          ob.matrix_world = mat_rot
         
          bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
          
          ob.rotation_euler=(math.pi/2,0.0,0.0)
         
        
        #if 'backFaceShown' in element.keys():
        #TODO    
        
        #object position and rotation 
        obs[0].dimensions=(dimX*scale,dimY*scale,dimZ*scale)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
        obs[0].location=(locX, locY, locZ)    
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        if 'angle' in element.keys():
          angle = element.get('angle') 
          obs[0].rotation_euler[2]=-float(angle)   

        if 'color' in element.keys():
          color = element.get('color') 
          r=int(color[2:4],16)/255.0
          g=int(color[4:6],16)/255.0
          b=int(color[6:8],16)/255.0
          bcolor=[r,g,b]
          for material in bpy.context.active_object.data.materials:
            material.diffuse_color=bcolor
  
        #search for texture or materials
        for prop in element:
          if prop.tag == 'texture':
              image=prop.get('image')
              for material in bpy.context.active_object.data.materials:
                  img = bpy.data.images.load(os.path.join(xml_path,image))
                  tex = bpy.data.textures.new(image, type = 'IMAGE')
                  tex.image = img        
                  mtex = material.texture_slots.add()
                  mtex.texture = tex
              
          if prop.tag == 'material':
              mname=prop.get('name')
              if 'color' in prop.keys():
                color = prop.get('color') 
                r=int(color[2:4],16)/255.0
                g=int(color[4:6],16)/255.0
                b=int(color[6:8],16)/255.0
                bcolor=[r,g,b]
                for material in bpy.context.active_object.data.materials:
                  if mname in material.name: 
                    material.diffuse_color=bcolor
        
              #face texture of material
              for texture in prop:
                if texture.tag == 'texture':  
                  image=texture.get('image')
                  for material in bpy.context.active_object.data.materials:
                     if mname in material.name: 
                       img = bpy.data.images.load(os.path.join(xml_path,image))
                       tex = bpy.data.textures.new(image, type = 'IMAGE')
                       tex.image = img        
                       mtex = material.texture_slots.add()
                       mtex.texture = tex  
           
      
      if objectName in ('light'):   
        owner=bpy.context.active_object    
       
        power= float(element.get('power'))       
  

        for light in element:
          if light.tag == 'lightSource':       
            color=light.get('color')
            r=int(color[2:4],16)/255.0
            g=int(color[4:6],16)/255.0
            b=int(color[6:8],16)/255.0
            bcolor=[r,g,b]
            lposx=(float(light.get('x'))-0.5)*dimX*scale*2.1
            lposy=(float(light.get('y'))-0.5)*dimY*scale*2.1
            lposz=(float(light.get('z'))-0.5)*dimZ*scale*2.1
                
            bpy.ops.object.lamp_add(type='POINT',location=(lposx, lposy, lposz))
            bpy.context.active_object.data.energy=4000.0*power*scale
            bpy.context.active_object.data.shadow_method='RAY_SHADOW'
            bpy.context.active_object.data.color=bcolor
            bpy.context.active_object.data.distance=10*scale
            bpy.context.active_object.parent=owner
            bpy.context.active_object.layers[3]= True
            bpy.context.active_object.layers[0]= False
            bpy.context.active_object.layers[1]= False
            bpy.context.active_object.layers[2]= False

        
    #insert camera  
      if objectName in ('observerCamera'): 
       if element.get('attribute') == 'observerCamera':
        locX = float(element.get('x'))*scale
        locY = -float(element.get('y'))*scale
        locZ = float(element.get('z'))*scale
        yaw = float(element.get('yaw'))
        pitch = float(element.get('pitch'))
        
        
        bpy.ops.object.camera_add(location=(locX, locY, locZ),rotation=((-pitch/8.0)+(-math.pi/2.0),math.pi,0))
        bpy.ops.mesh.primitive_cube_add(location=(locX, locY, locZ-(170.0*scale/2.0)),rotation=(0.0,0.0,-yaw))
        
        obs = bpy.context.selected_editable_objects[:] 
        bpy.context.scene.objects.active=obs[0]
        obs[0].name='player'
        obs[0].dimensions=(40*scale,20*scale,170.0*scale)
        
        bpy.data.objects["Camera"].parent=bpy.data.objects["player"]
        bpy.data.objects["Camera"].location=(0.0,-30.0*scale,22*scale)
        
        bpy.data.objects["player"].game.physics_type='CHARACTER'
        bpy.data.objects["player"].game.use_collision_bounds=True
        bpy.data.objects["player"].game.step_height=0.8
        
        
        #add logic blocks
        obj=bpy.data.objects["player"]
        cam=bpy.data.objects["Camera"]
        
        #foward
        bpy.ops.logic.sensor_add(type="KEYBOARD", object="player")
        bpy.ops.logic.controller_add(type="LOGIC_AND", object="player")
        bpy.ops.logic.actuator_add(type="MOTION", object="player")
        
        obj.game.sensors[-1].link(obj.game.controllers[-1])
        obj.game.actuators[-1].link(obj.game.controllers[-1])
        
        obj.game.sensors[-1].name="w"
        obj.game.sensors[-1].key="W"
        obj.game.actuators[-1].offset_location[1]=-speed
        
        #backward
        bpy.ops.logic.sensor_add(type="KEYBOARD", object="player")
        bpy.ops.logic.controller_add(type="LOGIC_AND", object="player")
        bpy.ops.logic.actuator_add(type="MOTION", object="player")
        
        obj.game.sensors[-1].link(obj.game.controllers[-1])
        obj.game.actuators[-1].link(obj.game.controllers[-1])
        
        obj.game.sensors[-1].name="s"
        obj.game.sensors[-1].key="S"
        obj.game.actuators[-1].offset_location[1]=speed
        
        #left
        bpy.ops.logic.sensor_add(type="KEYBOARD", object="player")
        bpy.ops.logic.controller_add(type="LOGIC_AND", object="player")
        bpy.ops.logic.actuator_add(type="MOTION", object="player")
        
        obj.game.sensors[-1].link(obj.game.controllers[-1])
        obj.game.actuators[-1].link(obj.game.controllers[-1])
        
        obj.game.sensors[-1].name="a"
        obj.game.sensors[-1].key="A"
        obj.game.actuators[-1].offset_location[0]=speed  
        
        #right
        bpy.ops.logic.sensor_add(type="KEYBOARD", object="player")
        bpy.ops.logic.controller_add(type="LOGIC_AND", object="player")
        bpy.ops.logic.actuator_add(type="MOTION", object="player")
        
        obj.game.sensors[-1].link(obj.game.controllers[-1])
        obj.game.actuators[-1].link(obj.game.controllers[-1])
        
        obj.game.sensors[-1].name="d"
        obj.game.sensors[-1].key="D"
        obj.game.actuators[-1].offset_location[0]=-speed        
        
        #jump
        bpy.ops.logic.sensor_add(type="KEYBOARD", object="player")
        bpy.ops.logic.controller_add(type="LOGIC_AND", object="player")
        bpy.ops.logic.actuator_add(type="MOTION", object="player")
        
        obj.game.sensors[-1].link(obj.game.controllers[-1])
        obj.game.actuators[-1].link(obj.game.controllers[-1])
        
        obj.game.sensors[-1].name="space"
        obj.game.sensors[-1].key="SPACE"
        obj.game.actuators[-1].mode='OBJECT_CHARACTER'
        obj.game.actuators[-1].use_character_jump=True
        
        #mouse view
        bpy.ops.logic.sensor_add(type="MOUSE", object="player")
        bpy.ops.logic.controller_add(type="LOGIC_AND", object="player")
        bpy.ops.logic.actuator_add(type="MOUSE", object="player")
      
        
        obj.game.sensors[-1].link(obj.game.controllers[-1])
        obj.game.actuators[-1].link(obj.game.controllers[-1])
        
        obj.game.sensors[-1].mouse_event='MOVEMENT'
        
        obj.game.actuators[-1].mode='LOOK'
        obj.game.actuators[-1].sensitivity_y=0.0
        
        
        
        bpy.ops.logic.actuator_add(type="MOUSE", object="Camera")
        cam.game.actuators[-1].link(obj.game.controllers[-1]) 
        
        cam.game.actuators[-1].mode='LOOK'
        cam.game.actuators[-1].sensitivity_x=0.0
        
        
    #Iterate over all members of the material struct and disable apha (to solve texture errors in blender game engine)
    for item in bpy.data.materials:
        if item.alpha == 1.0 :
           item.use_transparency = False
           item.use_transparent_shadows = True
        else:
           item.raytrace_mirror.use = True
           item.raytrace_mirror.reflect_factor= 0.1  
           item.diffuse_intensity= 0.01
 
           
    #better collision detection      
    bpy.data.scenes["Scene"].game_settings.physics_step_sub=5.0 
    
    #world settings
    bpy.data.worlds["World"].light_settings.use_ambient_occlusion=True
    bpy.data.worlds["World"].light_settings.ao_factor=0.01
    bpy.data.worlds["World"].light_settings.use_environment_light=True
    bpy.data.worlds["World"].light_settings.environment_energy=0.01
    
    bpy.data.scenes["Scene"].unit_settings.system='METRIC'
    bpy.data.scenes["Scene"].unit_settings.scale_length=0.01/scale
    bpy.data.scenes["Scene"].layers[0]=True
    bpy.data.scenes["Scene"].layers[1]=True
    bpy.data.scenes["Scene"].layers[2]=True
    bpy.data.scenes["Scene"].layers[3]=True
    
    return {'FINISHED'}


 
  def invoke(self, context, event):
      context.window_manager.fileselect_add(self)
      return {'RUNNING_MODAL'}
 
 
bpy.utils.register_class(OpenFile)
 
bpy.ops.object.openfile('INVOKE_DEFAULT')
