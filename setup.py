from distutils.core import setup

setup(
    name="AnanasStepperSDK",
    version = "1.0",
    description='The First Release, AnanasStepper SDK',
    author = "Gray Pillow",
    author_email="tickel.guan@gmail.com",
    py_modules = ['AnanasDevice', 'AnanasTools', 'SerialCon',
                  'SerialHelper', 'run_up_ananas_stepppers', 
                  'config_ananas_stepper']
    )