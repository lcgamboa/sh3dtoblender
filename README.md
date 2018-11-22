#   SweetHome3D <del>HTML5</del>/XML to Blender importer

## Video Tutorial

  https://youtu.be/ZwWan1RlQZY   

## How to use:
*   1-Open Sweethome 3D  http://www.sweethome3d.com
*   2-Create or open a existent house
*   3-Use the plugin <del>EXPORT to HTML5 or</del> EXPORT to XML/OBJ <del>http://www.sweethome3d.com/support/forum/viewthread_thread,6708</del>  http://www.sweethome3d.com/support/forum/viewthread_thread,6708_offset,20#29819
*   4-Open blender 
*   5-Choose Text Editor window and open <del>sh3d_html5_to_blender.py or</del> sh3d_xml_to_blender.py script
*   6-Run the script, in the File dialog choose the zip file generate by SweetHome 3D EXPORT to <del>HTML5</del> XML/OBJ plugin
   

 It's possible use the imported model with blender render and blender engine (the script add Logic blocks for FPS game like behavior)

 To render with blender cycles it's necessary import the materials. Try use https://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Material/Blender_Cycles_Materials_Converter

 The Sweethome 3D XML/OBJ file has ligth power information, the HTML5 format don't.  


## Attention

 Version 1.3.1 and above of the HTML export plugin no longer exports the object of the house structure and no more work with blender script.  
