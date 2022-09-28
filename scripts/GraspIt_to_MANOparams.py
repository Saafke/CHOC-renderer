# First, in one terminal: roslaunch graspit_interface graspit_interface.launch
# Perhaps earlier: source /home/xavier/graspit_ros_ws/devel/setup.bash

from graspit_commander import GraspitCommander
from kinematics import Kinematics
from grasp_utils import *
import os
import json

counter = 1

grasps_dict = {}

for cat in ["box", "stem", "nonstem"]:
    object_suffixes = os.listdir( os.path.join("/home/xavier/.graspit/worlds", cat) )
    object_suffixes.sort()
    
    for object_suffix in object_suffixes:

        print(counter, " - Current grasp:", object_suffix)

        # Load world via GraspitCommander (could also use GUI)
        GraspitCommander.clearWorld()
        GraspitCommander.loadWorld("{}/{}".format(cat, object_suffix[:-4]))

        # Get the kinematics
        kinematics = Kinematics('{}/models/robots/{}'.format(os.environ['GRASPIT'], 'ManoHand'))
        
        # Get robot (ManoHand in this case)
        response = GraspitCommander.getRobot()
        robot = response.robot
        
        # Get Grasp info
        body_name = object_suffix
        # quality = GraspitCommander.computeQuality()
        # print(quality)
        grasp = my_grasp_from_robot_state(robot, body_name, kinematics=kinematics)

        # Save to json file
        # with open(os.path.join('mano_outputs/{}.json'.format(body_name)), 'w') as f: \
        #     json.dump(grasp, f, indent=4, sort_keys=True)

        grasps_dict[counter] = grasp

        input("Inspect grasp, please. Press Enter to continue...")
        counter += 1

        with open(os.path.join('mano_outputs/grasp_dict.json'), 'w') as f:
            json.dump(grasps_dict, f, indent=4, sort_keys=True)

# Now we have the mano_pose parameters for all grasps.
# We know need to load the SMPL mesh with the mano hand, using these mano_pose parameters.
# Then remove all the rest of the body
# Save it as .glb