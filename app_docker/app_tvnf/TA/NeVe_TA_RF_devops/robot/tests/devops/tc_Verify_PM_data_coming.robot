*Settings*							
Documentation	In this test suite, PM data coming will be validated						
...							
...							
...	CUSTOM USERS/PASSWORDS PREREQUISITES:						
...	Variables you have to pass 4 parameters. \ - Any Ip of Netact node, except viis.						
...	- omc user and omc password						
...	- db_schema, like NOKLTE, SMAPMA...						
Suite Setup	Run Suite Setup Actions						
Test Teardown	Run Test Teardown Actions						
Force Tags	CRITICAL	INTEGRATE_NE	MULTI_NE_NEIW	devops			
Default Tags	VERIFY_PM						
Test Timeout	30 minutes						
Metadata	Author	Alex Zhao					
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
Library	Collections	#Resource	../resources/res_ssh_keywords.robot #Resource	../resources/res_neiw.robot			
Library	VerifyNewPMData.py						
							
*Variables*							
${PM_DATA_COMING}	False						
							
*Test Cases*							
Verify PM data coming	[Documentation]	This case aim to verify PM data coming.					
	[Tags]	VERIFY_PM					
	Log Variables	level=TRACE					
	VerifyNewPMData.connectPMNode	${Netact_ip}	${OMC_USER}	${OMC_PASSWORD}			
	${output}	VerifyNewPMData.runCmd	${db_schema}				
	VerifyNewPMData.writeTmpfile	${output}	PMrecord1				
	&{dict1}	VerifyNewPMData.getTableContent	PMrecord1	${db_schema}			
	: FOR	${n}	IN RANGE	7			
		log	${n}				
		sleep	150				
		${output1}	VerifyNewPMData.runCmd	${db_schema}			
		VerifyNewPMData.writeTmpfile	${output1}	PMrecord2			
		&{dict2}	VerifyNewPMData.getTableContent	PMrecord2	${db_schema}		
		${time1}	VerifyNewPMData.getRuncmdTime	PMrecord1			
		${time2}	VerifyNewPMData.getRuncmdTime	PMrecord2			
		${PM_DATA_COMING}=	comparePMdata	${dict1}	${dict2}	${db_schema}	
		run keyword if	${PM_DATA_COMING}==True	Exit for loop			
	run keyword if	${PM_DATA_COMING}==True	log	${db_schema} has PM data coming.			
	run keyword if	${PM_DATA_COMING}==False	Fail	${db_schema} has no PM data coming in last 15 mins.			
							
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
	Set Suite Variable	${db_schema}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_DB_SCHEMA}				
	Set Suite Variable	${Netact_ip}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_NETACT_HOST}				
	Set Suite Variable	${OMC_USER}	omc				
	Set Suite Variable	${OMC_PASSWORD}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_OMC_PASSWORD}				
							
Run Suite Teardown Actions	[Timeout]	4 minutes					
	SSHLibrary.Close All Connections						
	Run Keyword And Ignore Error	Monitor.Close Monitor If Running					
	Run Keyword And Ignore Error	Close CM Operations Manager If Running					
	Run Keyword And Ignore Error	My Kill Java Applications					
	Java Teardown Procedures						
							
My Kill Java Applications	OperatingSystem.Run	ps aux | grep -ie [j]nlp | awk '{print $2}' | xargs kill -9					
