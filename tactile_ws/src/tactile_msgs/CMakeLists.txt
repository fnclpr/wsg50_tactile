cmake_minimum_required(VERSION 3.8)
project(tactile_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/CalibrationStatus.msg"
  "msg/TactileProcessed.msg"
  DEPENDENCIES
  std_msgs
  geometry_msgs
  builtin_interfaces
)

ament_export_dependencies(
  rosidl_default_runtime
  std_msgs
  geometry_msgs
  builtin_interfaces
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # matches the existing repo's convention (uclv_tactile_interfaces/CMakeLists.txt)
  # of skipping the copyright/cpplint checks until license headers are finalized
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
