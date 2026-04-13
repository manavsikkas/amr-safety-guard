# AMR Safety Guard

Autonomous mobile robot safety platform for industrial environments. The robot patrols a facility, enforces restricted keepout zones via Nav2 costmaps, and triggers an emergency stop when YOLOv8 detects personnel in danger areas.

The system is split across two machines: a laptop running Gazebo Harmonic simulation and navigation, and an NVIDIA Jetson Orin Nano running real-time person detection. Both communicate over ROS2 topics.

## System Architecture

```
┌──────────────────────────────┐    ROS2 (LAN)    ┌──────────────────────────┐
│      Laptop  (Ubuntu 24.04)  │ ◄──────────────► │   Jetson Orin Nano       │
│                              │                  │                          │
│  Gazebo Harmonic             │                  │  YOLOv8n — CUDA 12.6     │
│  ├── industrial_world.sdf    │                  │  USB webcam              │
│  ├── amr_robot.urdf.xacro    │                  │  ROS2 Humble (Docker)    │
│  └── SLAM-generated map      │                  │  /person_detected topic  │
│                              │                  └──────────────────────────┘
│  Nav2 + SLAM Toolbox         │
│  ├── 4-waypoint patrol loop  │
│  ├── Keepout zone costmap    │
│  ├── Zone violation monitor  │
│  └── Emergency stop handler  │
└──────────────────────────────┘
```

## Features

- **Autonomous Patrol** — robot follows a 4-waypoint rectangular path continuously
- **Keepout Zones** — Nav2 costmap filter blocks the robot from entering defined danger areas
- **Zone Monitor** — detects when the robot enters a danger zone via odometry
- **Person Detection** — YOLOv8n detects humans in real-time from webcam feed
- **Emergency Stop** — robot halts for 5 seconds on person detection, then resumes patrol
- **Missed Waypoint Logging** — identifies whether a missed waypoint was blocked by path or danger zone

## Stack

| Component | Technology |
|---|---|
| Simulation | Gazebo Harmonic |
| Navigation | ROS2 Jazzy + Nav2 |
| Mapping | SLAM Toolbox |
| Perception | YOLOv8n + cv_bridge |
| Compute (perception) | NVIDIA Jetson Orin Nano |
| Robot OS (Jetson) | ROS2 Humble (Docker) |
| GPU Inference | CUDA 12.6 + PyTorch 2.4 |

## Package Structure

```
amr-safety-guard/
├── src/amr_safety_guard/
│   ├── amr_safety_guard/
│   │   ├── patrol_node.py        # Waypoint patrol — Nav2 action client, goal sequencing
│   │   ├── zone_monitor.py       # Odometry-based zone violation detector
│   │   ├── keepout_mask.py       # Keepout zone costmap filter configuration
│   │   ├── emergency_stop.py     # Halts robot 5 s on person detection, then resumes
│   │   ├── person_detector.py    # YOLOv8n inference, publishes /person_detected
│   │   └── webcam_publisher.py   # Streams webcam to ROS2 image topic
│   ├── launch/
│   │   ├── navigation.launch.py  # Full system launch (Nav2 + patrol + monitoring)
│   │   ├── simulation.launch.py  # Gazebo Harmonic + robot spawn
│   │   ├── slam.launch.py        # SLAM mapping mode
│   │   └── rsp.launch.py         # Robot state publisher only
│   ├── config/
│   │   ├── nav2_params.yaml                   # Nav2 planner + costmap config
│   │   └── mapper_params_online_async.yaml    # SLAM Toolbox parameters
│   ├── maps/
│   │   ├── industrial_map.yaml   # Pre-generated SLAM map
│   │   └── keepout_mask.yaml     # Keepout zone overlay mask
│   ├── urdf/
│   │   └── amr_robot.urdf.xacro  # Custom AMR robot model
│   ├── worlds/
│   │   └── industrial_world.sdf  # Gazebo Harmonic simulation world
│   └── rviz/
│       └── rviz_config.rviz      # RViz2 visualisation layout
├── jetson/
│   └── Dockerfile.perception     # Jetson container: ROS2 Humble + PyTorch + YOLOv8
└── README.md
```

## Running the Simulation

```bash
# Build
cd ~/amr_ws
colcon build --packages-select amr_safety_guard
source install/setup.bash

# Launch full system
ros2 launch amr_safety_guard navigation.launch.py

# Manually trigger emergency stop (for testing)
ros2 topic pub /person_detected std_msgs/msg/String "data: 'Human detected: 0.95'" --once
```

## Jetson Setup (Perception)

```bash
# Build perception container
docker build --network host -t amr_perception:latest -f jetson/Dockerfile.perception .

# Run with GPU + webcam
docker run -it --rm --runtime nvidia --network host \
  --device /dev/video0 \
  -v ~/amr_ws:/workspace \
  amr_perception:latest bash

# Inside container
colcon build --packages-select amr_perception
source install/setup.bash
ros2 run amr_perception person_detector
```

## Hardware

| Device | Role |
|---|---|
| Gaming laptop (WSL2 Ubuntu 24.04) | Simulation, navigation, map serving |
| NVIDIA Jetson Orin Nano | Real-time YOLOv8n inference (CUDA) |
| USB webcam | Camera input for person detection |
| Arduino Uno + L298N | Hardware-level emergency stop (in progress) |

## License

MIT