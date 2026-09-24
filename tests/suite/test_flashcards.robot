*** Settings ***
Documentation    Test cases for flash-cards snap
Resource         kvm.resource


*** Test Cases ***
Flash Cards Launches And Renders
    [Documentation]    Verify flash-cards snap launches and renders a UI on Mir
    [Tags]    smoke    yarf:certification_status: blocker
    Log Screenshot
