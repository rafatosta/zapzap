cmake_minimum_required(VERSION 3.16)

project(ZapZap)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets)
find_package(Qt6 COMPONENTS WebEngineWidgets)

add_executable(zapzap
    src/main.cpp
    src/MainWindow.cpp
    src/MainWindow.h
)

if (Qt6WebEngineWidgets_FOUND)
    target_compile_definitions(zapzap PRIVATE HAVE_QTWEBENGINEWIDGETS)
    target_link_libraries(zapzap
        Qt6::Widgets
        Qt6::WebEngineWidgets
    )
else()
    message(WARNING "Qt6 WebEngineWidgets not found. Building fallback UI without embedded web view.")
    target_link_libraries(zapzap
        Qt6::Widgets
    )
endif()
