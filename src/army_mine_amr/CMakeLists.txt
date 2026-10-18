cmake_minimum_required(VERSION 3.8)
project(army_mine_amr)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(visualization_msgs REQUIRED)

# Install directories
install(DIRECTORY
  urdf
  meshes
  config
  launch
  rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install python scripts
install(PROGRAMS
  scripts/amr_mine_defusal_controller.py
  scripts/amr_mine_laying_controller.py
  scripts/amr_teleop_keyboard.py
  scripts/gz_harmonic_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
