*** Settings ***
Documentation     This test suite will integrate NTHLRFE NE to NetAct via NEIW
...
...               Integration > Integrating NT HLR FE to NetAct.
Suite Setup       Suite Setup Actions
Suite Teardown    Suite Teardown Action
Test Teardown     Test Teardown Actions
Force Tags        CRITICAL    INTEGRATE_NE    NTHLRFE_NEIW
Default Tags      DEVOPS
Library           RemoteSwingLibrary
Library           Screenshot    screenshot_module=PyGTK
Library           String
Resource          ../resources/res_ssh_keywords.robot
Library           Collections
Resource          ../resources/res_neiw.robot
Resource          ../resources/res_netact_applications.robot
Resource          ../resources/res_monitor_keywords.robot
Resource          ../resources/res_cm_cmop.robot
Resource          ../resources/res_alarms.robot
Resource          ../resources/res_neac.robot
Resource          ../resources/res_dynamic_adaptation_keyword.robot
Resource          ../resources/res_element_integration.robot

*** Variable ***
@{LOGIN}          ${SDV_DESKTOP_ADMIN_USER}    ${SDV_DESKTOP_ADMIN_PASSWORD}
@{groups}         sysop    tagroup    sysop8
${scope}          MRC-${EDV_NTHLRFE_MRC_INSTANCE}/MR-${EDV_NTHLRFE_MR_INSTANCE}
@{USERNAMES}      ${EDV_NTHLRFE_WSUSER_LAN_USERNAME}    ${EDV_NTHLRFE_WSUSER_LAN_USERNAME}    ${EDV_NTHLRFE_OAM_LAN_USERNAME}    ${EDV_NTHLRFE_OAM_LAN_USERNAME}    ${EDV_NTHLRFE_OAM_LAN_USERNAME}    ${EDV_NTHLRFE_WSUSER_LAN_USERNAME}
@{SERVICE_TYPES}    HTTP Access    HTTPS Access    SSH Access    SS7 Access    Remote MML Access    Web Service Access
@{PASSWORDS}      ${EDV_NTHLRFE_WSUSER_LAN_PASSWORD}    ${EDV_NTHLRFE_WSUSER_LAN_PASSWORD}    ${EDV_NTHLRFE_OAM_LAN_PASSWORD}    ${EDV_NTHLRFE_OAM_LAN_PASSWORD}    ${EDV_NTHLRFE_OAM_LAN_PASSWORD}    ${EDV_NTHLRFE_WSUSER_LAN_PASSWORD}
${NE_INTEGRATION_SUCCEEDED}    True
${NE_TYPE}        EDV_NTHLRFE_NE_CLASS

*** Test Cases ***
Create MR
    Element Integration.Create MRC Object If It Does Not Exist    ${EDV_NTHLRFE_MRC_INSTANCE}
    Element Integration.Create MR Object If It Does Not Exist    ${EDV_NTHLRFE_MRC_INSTANCE}    ${EDV_NTHLRFE_MR_INSTANCE}
    Comment    ${META_DIRECTORY}    Set Variable If    '${EDV_NTHLRFE_NE_SW}'=='16.0'    /global/esymac/Ines_o2ml    /global/esymac
    comment    test

Create SFTP user in NEAC
    [Documentation]    This test case creates the SFTP Access credential in Network Element Access Control to enable the communication for the support of Dynamic Adaptation.
    [Tags]    NEAC    USER_CREATION
    Run Keyword If    '${NE_INTEGRATION_SUCCEEDED}' == 'false'    Fail    Service Users will not be created since there was a failure.
    Open Network Element Access Control    @{OMC_LOGIN}
    Check If NEAC Is Opened Properly    5
    Filter Scope In Credentials    ${scope}
    ${existingServices}=    Get Existing Service Types
    ${status}=    Run Keyword And Return Status    List Should Not Contain Value    ${existingServices}    SFTP Access
    ${row}=    Run Keyword if    '${status}' == 'False'    Get Index From List    ${existingServices}    SFTP Access
    Run Keyword if    '${status}' == 'False'    Verify Correct Group    ${row}    @{groups}
    Run Keyword If    '${status}' == 'False'    NeVe.Screenshot    SFTP_user_exists
    Run Keyword If    '${status}' == 'False'    Pass Execution    SFTP user already exists.
    ${user_created}=    Create New User    ${EDV_NTHLRFE_OAM_LAN_USERNAME}    SFTP Access    ${scope}    ${EDV_NTHLRFE_OAM_LAN_PASSWORD}
    ${status}=    Run Keyword And Return Status    List Should Contain Value    ${existingServices}    SFTP Access
    Run Keyword if    '${user_created}' == 'False'    FAIL    SFTP Access user was not created!
    ${existingServices}=    Get Existing Service Types
    ${row}=    Run Keyword if    '${status}' == 'True'    Get Index From List    ${existingServices}    SFTP Access
    Run Keyword if    '${user_created}' == 'True'    Grant Credentials    0    @{groups}    sysop    cmauto
    Run Keyword If    '${user_created}' == 'True'    NeVe.Screenshot    nwi3_user_created
    ...    ELSE    FAIL    User was not created correctly!
    Close Network Element Access Control

Create NEAC Service Users
    [Documentation]    This test case checks whether the needed credentials for NE integration are created. If not, it creates the credentials.
    [Tags]    NEAC    USER_CREATION
    Run Keyword If    '${NE_INTEGRATION_SUCCEEDED}' == 'false'    Fail    Service Users not \ created since there was a failure.
    Comment    Select Window With Title Containing    ${NETWORK_ELEMENT_ACCESS_CONTROL_ALIAS}
    Open Network Element Access Control    @{OMC_LOGIN}
    Check If NEAC Is Opened Properly    5
    Filter Scope In Credentials    ${scope}
    ${existingServices}=    Get Existing Service Types
    ${SERVICE_TYPES}    ${USERNAMES}    ${PASSWORDS}=    Remove Duplicate Entries In Service Types    ${existingServices}    ${SERVICE_TYPES}    ${USERNAMES}
    ...    ${PASSWORDS}
    ${existingLen}=    Get Length    ${existingServices}
    Run Keyword If    ${existingLen} > 0    Verify Groups For Services    ${existingServices}
    ${serviceLen}=    Get Length    ${SERVICE_TYPES}
    Run Keyword If    ${serviceLen} > 0    Create Users For Service Types    ${SERVICE_TYPES}    ${USERNAMES}    ${PASSWORDS}
    Input Text    //*[@id="credentialList:dataTable:cstFilterBox"]    ${SPACE}
    Wait Until Keyword Succeeds    ${DEF_NEAC_TIMEOUT}    ${DEF_NEAC_RETRY}    Page Should Not Contain    Results: 1
    Close Network Element Access Control

NTHLRFE NEIW
    [Documentation]    In this test case, NEIW for LTE OMS is executed.
    [Tags]    NEIW
    ${M_D}    Set Variable If    '${EDV_NTHLRFE_NE_SW}'=='16.0'    /global/esymac/Ines_o2ml    /global/esymac
    Set Suite Variable    ${Meta_Directory}    ${M_D}
    Run Keyword Unless    ${NE_INTEGRATION_SUCCEEDED}    Fail    NTHLRFE NEIW test case is not executed as NTHLRFE Integration was not successful.
    : FOR    ${i}    IN RANGE    1
    \    ${status}    Run Keyword And Return Status    NEIW.Integrate NTHLRFE    ${NE_TYPE}
    \    Exit For Loop If    ${status}
    Run Keyword Unless    ${status}    FAIL    NEIW integration has failed!

Configuring SSH connection between NTHLRFE and NetAct
    [Documentation]    This test case configures SSH connection between NT HLR FE and NetAct.
    [Tags]    SSH_CONNECTION
    Run Keyword If    '${NE_INTEGRATION_SUCCEEDED}' == 'false'    Fail    SSH connection not established since there was a failure
    Element Integration.Configuring SSH connection IMS    ${NE_TYPE}

Verify Alarm Upload
    [Documentation]    This test case uploads alarm for NTHLRFE managed object and verifies if it is successful.
    [Tags]    MONITOR    ALARM_UPLOAD    VERIFY
    Run Keyword If    '${NE_INTEGRATION_SUCCEEDED}' == 'false'    Fail    Verify Alarm Upload not executed since there was failure
    Monitor.Alarm Upload    PLMN-${EDV_PLMN_INSTANCE}/${EDV_NTHLRFE_NE_CLASS}-${EDV_NTHLRFE_NE_INSTANCE}    ${SDV_DESKTOP_ADMIN_USER}

Verify CM Upload
    [Documentation]    This test case verifies configuration management in CM Operations Manager for successful NE integration.
    [Tags]    CMOP    CM_UPLOAD    VERIFY
    Run Keyword If    '${NE_INTEGRATION_SUCCEEDED}' == 'false'    Fail    Verify Alarm Upload and CM Upload not executed since there was failure
    ${status}    ${operation_name}    CMOP.CM Upload    NTHLRFE    TA_Upload_NTHLRFE
    Run Keyword If    '${status}' == 'PASS'    Log    CM upload operation '${operation_name}' has been succesfully finished
    Run Keyword Unless    '${status}' == 'PASS'    Fail    CM upload operation '${operation_name}' has NOT been succesfully finished
    Close CM Operations Manager

*** Keyword ***
Test Teardown Actions
    SSHLibrary.Close All Connections
    Run Keyword If Test Failed    Set Suite Variable    ${NE_INTEGRATION_SUCCEEDED}    false
    Run Keyword If Test Failed    NeVe.Screenshot    Teardown
    Run Keyword If Test Failed    Run Keyword And Ignore Error    Monitor.Close Monitor If Running
    Run Keyword If Test Failed    Close All Browsers
    Run Keyword If Test Failed    OperatingSystem.Run    ps aux | grep -ie [j]nlp | awk '{print $2}' | xargs kill -9

Suite Teardown Action
    SSHLibrary.Close All Connections
    Run Keyword And Ignore Error    Monitor.Close Monitor If Running
    Run Keyword And Ignore Error    Close CM Operations Manager If Running
    Comment    Run Keyword And Ignore Error    My Kill Java Applications
    Java Teardown Procedures

Suite Setup Actions
    Should Match Regexp    ${EDV_NTHLRFE_NE_SW}    [1-9][6-9]\.(0|5)C    NEIW integration is supported for Nthlrfe 16.5C onwards. With older SW please use ordinary NTHLR integration.    False
    Java Setup Procedures
    SeleniumLibrary.Register Keyword To Run On Failure    No Operation
    Overwrite EDV MR variable when users are not default    ${NE_TYPE}
