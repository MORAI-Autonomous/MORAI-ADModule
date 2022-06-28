# MORAI - AD Module

AD (Autonomous Drive) Module is a vehicle control core module which plan the path and lateral / longitudinal control the vehicle.


This repository cannot run alone.

Please checkout the network wrapper repository with [ROS](https://github.com/MORAI-Autonomous/MORAI-DriveExample_ROS) or [UDP](https://github.com/MORAI-Autonomous/MORAI-DriveExample_UDP)

```
./
├── config                          # [Config] about configuration file to autonomous drive 
│    ├── map                          # desired trajectory datas directory
│    ├── config.json                  # configuration parameters file
│    └── config.py                    # load and apply the config.json file script
├── control                         # [Control] about vehicle control
│    ├── control_input.py             # convert and apply to the actual control input
│    ├── pid.py                       # calculate the longitudinal control input with PID
│    └── pure_pursuit.py              # calculate the lateral control input with pure pursuit
├── localization                    # [Localization] about localization the current vehicle position
│    └── path_manager.py              # make local path which from the global path with Mgeo or defined trajectories
├── mgeo                            # [HD Map] about datas and process with HD map
│    ├── lib                          # directory about MGeo HD map data
│    │    ├── mgeo                      # MGeo HD map loader repo (submodule)
│    │    └── mgeo_data                 # directory about drivalble example map
│    ├── calc_mgeo_path.py            # dijkstra path finder wrapper
│    ├── e_dijkstra.py                # dijkstra algorithm
│    ├── get_mgeo.py                  # MGeo loader wrapper
│    └── mgeo_pub.py                  # ROS2 MGeo HD map data publisher
├── perception                      # [Perception] classify and filter the objects
│    ├── forward_object_detector.py   # filter objects by driving path about ego vehicle
│    └── object_info.py               # classifying the object information
├── planning                        # [Planning] planning the driving vehicle
│    └── adaptive_cruise_control.py   # planning the velocity to smart/adaptive cruise control
├── autonomous_driving.py           # [Entry] autonomous driving example class with above functions
└── vehicle_state.py                # [Status] vechile status information
```


## More information

If you not use our simulator yet, please visit [our homepage](https://www.morai.ai/) and check out the MORAI Simulator!

Or if you use already, please check the [MORAI Sim manual (EN)](https://help-morai-sim-en.scrollhelp.site/) / [MORAI Sim manual (KR)](https://help-morai-sim.scrollhelp.site/).

# License
- AD Module license info:  [AD module License](./docs/License.md)

