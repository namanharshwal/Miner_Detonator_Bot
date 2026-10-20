cmake_minimum_required(VERSION 3.8)
project(mountain_grassland_world)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

# Install directories
install(DIRECTORY
  launch
  worlds
  models
  materials
  config
  rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install python scripts
install(PROGRAMS
  scripts/grassland_mine_tracker_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
