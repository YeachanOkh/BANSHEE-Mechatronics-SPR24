import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ubuntu/BANSHEE-Mechatronics-SPR24/Banshee-ros/install/camera_node'
