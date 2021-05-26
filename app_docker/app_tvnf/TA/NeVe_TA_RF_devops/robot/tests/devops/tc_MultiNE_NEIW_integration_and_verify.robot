*Settings*							
Documentation	In this test suite, Network element is integrated to NetAct via NEIW.						
...							
...							
...	CUSTOM USERS/PASSWORDS PREREQUISITES:						
...	Variables you have to overwrite/write in ElementDataVariables.xml						
Suite Setup	Run Suite Setup Actions						
Test Teardown	Run Test Teardown Actions						
Force Tags	CRITICAL	INTEGRATE_NE	MULTI_NE_NEIW	devops			
Test Timeout	30 minutes						
Metadata	Author	Jessica Zeng					
Library	AutoIntegrationMultiNE.py	INTENE					
Resource	../resources/res_neac.robot						
Resource	../resources/res_alarms.robot						
Resource	../resources/res_common_variables.robot						
Resource	../resources/res_monitor_keywords.robot						
Resource	../resources/res_netact_applications.robot						
Library	RemoteSwingLibrary						
Resource	../resources/res_element_integration.robot						
Resource	../resources/res_ssh_connections.robot						
Resource	../resources/res_cm_cmop.robot						
Library	Screenshot	screenshot_module=PyGTK					
Library	String						
Library	VerifyParams.py						
Library	Collections	#Resource	../resources/res_ssh_keywords.robot #Resource	../resources/res_neiw.robot			
							
*Variables*							
${NE_INTEGRATION_SUCCEEDED}	True						
${NE_INTEGRATION_VERIFICATION_SUCCEEDED}	True						
@{LOGIN}	omc	omc	#${SDV_DESKTOP_ADMIN_USER} | ${SDV_DESKTOP_ADMIN_PASSWORD}				
&{input_param_list}	ne_type=${EDV_MRBTS_NE_TYPE}	ne_version=${EDV_MRBTS_NE_SW}	SDV_OSS_WAS_DMGR_IP=${EDV_MRBTS_SDV_OSS_WAS_DMGR_IP}	NETACT_HOST=${EDV_MRBTS_NETACT_HOST}	NETACT_LBWAS=${EDV_MRBTS_NETACT_LBWAS}	DN=${EDV_MRBTS_DN}	OMC_USERNAME=omc
...	OMC_PASSWORD=${EDV_MRBTS_OMC_PASSWORD}	MR=${EDV_MRBTS_MR}	MRBTS address=${EDV_MRBTS_MRBTS_ADDRESS}	MRBTS distinguished name=${EDV_MRBTS_DN}	NE3SWS agent security mode=${EDV_MRBTS_NE3SWS_AGENT_SECURITY_MODE}	MRBTS EM address=${EDV_MRBTS_MRBTS_EM_ADDRESS}	IP Version=${EDV_MRBTS_IP_VERSION}
...	credentials=${None}	agent HTTPS connection port=${EDV_MRBTS_NE3SWS_AGENT_HTTPS_CONNECTION_PORT}					
							
*Test Cases*							
Integrate NE through NEIW	[Documentation]	In this test case, NEIW integration interface for NE is executed.					
	[Tags]	devops	NEIW_only	MULTI_NE_NEIW			
	[Timeout]	30 minutes					
	Log Variables	level=TRACE					
	${neiw_template_name }=	AutoIntegrationMultiNE .get_neiw_template_file_name	&{input_param_list}[ne_type]	&{input_param_list}[ne_version]			
	AutoIntegrationMultiNE.set_remote_template_file_and_ne_type	${neiw_template_name}	&{input_param_list}[ne_type]	${input_param_list}			
	${Is_Integration_Success}=	Wait Until Keyword Succeeds	3x	200ms	AutoIntegrationMultiNE .integrate_NE	${input_param_list}	
	Run Keyword Unless	${Is_Integration_Success}	Fail	NE Integration action is not successful.	#Fail or False?		
							
*Keywords*							
Run Test Teardown Actions	[Timeout]	2 minutes					
	########## Test Setup and Teardown keywords ##########						
	SSHLibrary.Close All Connections						
	Run Keyword If Test Failed	Set Suite Variable	${NE_INTEGRATION_SUCCEEDED}	False			
	Run Keyword If Test Failed	NeVe.Screenshot	Teardown				
	Run Keyword If Test Failed	Run Keyword And Ignore Error	Monitor.Close Monitor If Running				
	Run Keyword If Test Failed	Close All Browsers					
	Run Keyword If Test Failed	OperatingSystem.Run	ps aux | grep -ie [j]nlp | awk '{print $2}' | xargs kill -9				
							
Run Suite Setup Actions	[Timeout]	10 minutes					
	#the following disables automatic screenshots that are taken by seleniumlibrary						
	SeleniumLibrary.Register Keyword To Run On Failure	No Operation					
	Java Setup Procedures						
	${null_value_exist}=	VerifyParams.exist_null_params	${input_param_list}				
	Run Keyword Unless	${null_value_exist}	Fail	Params exist null value.			
	${mr_format_correct}=	VerifyParams.verify_mr_format	${input_param_list}				
	Run Keyword Unless	${mr_format_correct}	Fail	MR format is not correct			
	VerifyParams.process_ne_presentation_name	${input_param_list}					
	VerifyParams.process_credentials	${input_param_list}					
							
Run Suite Teardown Actions	[Timeout]	4 minutes					
	SSHLibrary.Close All Connections						
	Run Keyword And Ignore Error	Monitor.Close Monitor If Running					
	Run Keyword And Ignore Error	Close CM Operations Manager If Running					
	Run Keyword And Ignore Error	My Kill Java Applications					
	Java Teardown Procedures						
							
My Kill Java Applications	OperatingSystem.Run	ps aux | grep -ie [j]nlp | awk '{print $2}' | xargs kill -9					
