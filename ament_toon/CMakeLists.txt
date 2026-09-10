cmake_minimum_required(VERSION 3.8)
project(ament_toon)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# #To avoid problem on early check of existance of this directory
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/include)

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(LAPACK REQUIRED)

include(ExternalProject)
ExternalProject_Add(upstream_igh_eml    # Name for custom target
# #--Download step--------------
  GIT_REPOSITORY https://github.com/edrosten/TooN.git 
  GIT_TAG TOON_3.2
  TIMEOUT 30           # Time allowed for file download operations
# #--Configure step-------------
  CONFIGURE_COMMAND <SOURCE_DIR>/configure --prefix=<INSTALL_DIR>
# #--Build step-----------------
  BUILD_IN_SOURCE 1         # Use source dir for build dir
# #--Install step---------------
  INSTALL_DIR ${CMAKE_INSTALL_PREFIX}           # Installation prefix
  )

  ament_export_include_directories(${CMAKE_INSTALL_PREFIX}/include)

ament_package()
