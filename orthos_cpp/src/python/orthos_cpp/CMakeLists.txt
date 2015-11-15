

#--------------------------------------------------------------
# Add Library
#--------------------------------------------------------------
add_library( _orthos_cpp SHARED
    orthos_cpp.cxx
    #extend_qt.cxx
    layer.cxx
)
#--------------------------------------------------------------
# Link libraries
#--------------------------------------------------------------
find_library(RT rt)
target_link_libraries( _orthos_cpp
    ${PYTHON_LIBRARIES}
    ${Boost_PYTHON_LIBRARIES}
)

if("${Boost_PYTHON_LIBRARY}" MATCHES "boost_python\\.lib")
    ADD_DEFINITIONS(-DBOOST_AUTO_LINK_NOMANGLE)
endif()


IF(PYTHON_PLATFORM MATCHES "windows$" OR WIN32)
    SET_TARGET_PROPERTIES( _orthos_cpp PROPERTIES OUTPUT_NAME "_orthos_cpp" PREFIX "" SUFFIX ".pyd")
ELSEIF(APPLE)
    SET_TARGET_PROPERTIES( _orthos_cpp PROPERTIES OUTPUT_NAME "_orthos_cpp" PREFIX "" SUFFIX ".so")
ELSE()
    SET_TARGET_PROPERTIES( _orthos_cpp PROPERTIES OUTPUT_NAME "_orthos_cpp" PREFIX "")
ENDIF()


file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py  DESTINATION ${CMAKE_CURRENT_BINARY_DIR} )

install(FILES __init__.py
        DESTINATION ${PYTHON_SITE_PACKAGES}/orthos_cpp)

IF(PYTHON_PLATFORM MATCHES "windows$" OR WIN32)
    install(TARGETS _orthos_cpp
            RUNTIME DESTINATION ${PYTHON_SITE_PACKAGES}/orthos_cpp)
ELSE()
    install(TARGETS _orthos_cpp
            LIBRARY DESTINATION ${PYTHON_SITE_PACKAGES}/orthos_cpp)
ENDIF()

