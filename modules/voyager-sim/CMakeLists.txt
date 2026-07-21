cmake_minimum_required(VERSION 3.10)
project(voyager_sim VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compile flags
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -O2)
endif()

# Include directories
include_directories(include)

# Define library
add_library(voyager_sim
    src/RigidBody.cpp
    src/SensorModels.cpp
)

# Test target
add_executable(test_rigidbody
    tests/test_rigidbody.cpp
)
target_link_libraries(test_rigidbody PRIVATE voyager_sim)
