import pybullet as p
import pybullet_data
import time
import os
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)
plane = p.loadURDF("plane.urdf")
robot_urdf = os.path.join(os.getcwd(), "go1.urdf")
if not os.path.exists(robot_urdf):
    print("ERROR: go1.urdf not found in the current directory. Please download the Unitree Go1 URDF and place it here.")
    exit(1)
robot = p.loadURDF(robot_urdf, [0, 0, 0.3])
try:
    for _ in range(2400):
        p.stepSimulation()
        time.sleep(1./240.)
finally:
    p.disconnect()
