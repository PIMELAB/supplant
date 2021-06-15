# supplant
Python module to replace variables and generate a full factorial design.

How to use
----------

Considering a folder called 'skeletonFolder' containing the 'base_case.txt' file.

*base_case.txt*:
```
mass = __MASS__
velocity_x = __VELOCITY_X__
velocity_y = _VELOCITY_Y__
force_x = __FORCE_X__
```

You want to create new cases based on this layout, replacing the mass value by a constant, the velocity_x and velocity_y by a list, and force_x by a list dependent on velocity_x. You proceed with the following implementation:

*example.py*:
```python
import supplant

sim = supplant.Configuration('skeletonFolder')
sim.add_constant('__MASS__', 1)
sim.add_variable('__VELOCITY_X__', [0.2, 0.4])
sim.add_variable('__VELOCITY_Y__', [-0.1, -0.5])
sim.add_dependent('__FORCE_X__', [200, 400], '__VELOCITY_X__')
sim.write_configurations()
```

The final output will be 4 new cases (case_0 to case_3) containing the desired values.
