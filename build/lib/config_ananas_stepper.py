
from AnanasStepperSDK import AnanasDevice

myAnanas = AnanasDevice.AnanasManager()
myAnanas.default_config()

if not myAnanas.start_ananas():
    exit(1)

# 1. 配置 AnanasSteper的编号；CAN 波特率 485 波特率 细分数了 ）
# 1. Set Config of AnanasStepper
myAnanas.set_can_baudrate(500000)
myAnanas.set_motion_index(1)
myAnanas.set_485_baudrate(115200)
myAnanas.set_step_subdevide(128)
myAnanas.set_current(1)

