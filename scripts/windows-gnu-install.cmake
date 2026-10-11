# Unicorn 2.1.5 only installs its combined static library with LEGACY enabled.
# Build that same ARM archive from its existing object targets, without the symlink.
# This hook avoids modifying the downloaded dependency or requiring Administrator.
if(PROJECT_NAME STREQUAL "unicorn")
    function(zeebx_install_unicorn)
        set_target_properties(unicorn PROPERTIES OUTPUT_NAME "unicorn-components")
        add_library(zeebx_unicorn STATIC
            $<TARGET_OBJECTS:unicorn>
            $<TARGET_OBJECTS:unicorn-common>
            $<TARGET_OBJECTS:arm-softmmu>)
        set_target_properties(zeebx_unicorn PROPERTIES OUTPUT_NAME "unicorn")
        install(TARGETS zeebx_unicorn ARCHIVE DESTINATION lib)
    endfunction()
    cmake_language(DEFER CALL zeebx_install_unicorn)
endif()
