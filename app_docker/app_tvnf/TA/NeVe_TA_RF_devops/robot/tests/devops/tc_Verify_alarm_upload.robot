*Settings*							
Documentation	In this test suite, Alarm upload will be triggered by fmCLI.sh						
...							
...	For more details: http://belk.netact.noklab.net/N1X_TRUNK/index.jsp?topic=%2Ffm_command_line_operations%2Fconcepts%2Fcommand_line_overview.html						
...							
...							
...							
...	CUSTOM USERS/PASSWORDS PREREQUISITES:						
...	Variables you have to pass 4 parameters.						
...	- Any netact node ip except viis.						
...	- omc user and omc password						
...	- root user and root password						
...	- dn, like PLMN-PLMN/MRBTS-xxx						
Suite Setup	Run Suite Setup Actions						
Test Teardown	Run Test Teardown Actions						
Force Tags	CRITICAL	INTEGRATE_NE	MULTI_NE_NEIW	devops			
Default Tags	VERIFY_AUP						
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
Library	TriggerAlarmUpload.py						
							
*Variables*							
${aupstatus}	False						
							
*Test Cases*							
Alarm upload by fmCLI	[Documentation]	This case aim to verify PM data coming.					
	[Tags]	VERIFY_AUP					
	Log Variables	level=TRACE					
	TriggerAlarmUpload.connectSpecificNode	${Netact_ip}	${ROOT_USER}	${ROOT_PASSWORD}			
	Comment	${output}	TriggerAlarmUpload.checkCertStatus				
	Comment	TriggerAlarmUpload.writeintoTmpfile	${output}	aup_omc_certStatus.txt			
	Comment	${is_omc_cert_exists}	TriggerAlarmUpload.getomccert	aup_omc_certStatus.txt			
	Comment	run keyword if	${is_omc_cert_exists}==False	TriggerAlarmUpload.creatcert2omc			
	TriggerAlarmUpload.creatcert2omc						
	TriggerAlarmUpload.connectdmgrNode	${OMC_USER}	${OMC_PASSWORD}				
	${output1}	TriggerAlarmUpload.executeaupbyfmcli	${dn}				
	TriggerAlarmUpload.writeintoTmpfile	${output1}	aup_jobid.txt				
	${jobid}	TriggerAlarmUpload.getjobid	aup_jobid.txt				
	log	${jobid}					
	: FOR	${n}	IN RANGE	5			
		log	${n}				
		sleep	60				
		${aupstatus}	TriggerAlarmUpload.getaupstatus	${jobid}			
		log	${aupstatus}				
		run keyword if	'${aupstatus}'=='True'	Exit for loop			
		run keyword if	'${aupstatus}'=='False'	Exit for loop			
		run keyword if	'${aupstatus}'=='RUNNING'	Continue For Loop			
	run keyword if	'${aupstatus}'=='True'	log	Alarm upload succeed.			
	run keyword if	'${aupstatus}'=='False'	Fail	Alarm upload failed.			
	run keyword if	'${aupstatus}'=='RUNNING'	Fail	Alarm upload can't end normally.			
							
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
	Set Suite Variable	${dn}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_DN}				
	Set Suite Variable	${Netact_ip}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_NETACT_HOST}				
	Set Suite Variable	${OMC_USER}	omc				
	Set Suite Variable	${OMC_PASSWORD}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_OMC_PASSWORD}				
	Set Suite Variable	${ROOT_USER}	root				
	Set Suite Variable	${ROOT_PASSWORD}	${EDV_${EDV_NE_CLASS_UNDER_TEST}_ROOT_PASSWORD}				
							
Run Suite Teardown Actions	[Timeout]	4 minutes					
	SSHLibrary.Close All Connections						
	Run Keyword And Ignore Error	Monitor.Close Monitor If Running					
	Run Keyword And Ignore Error	Close CM Operations Manager If Running					
	Run Keyword And Ignore Error	My Kill Java Applications					
	Java Teardown Procedures						
							
My Kill Java Applications	OperatingSystem.Run	ps aux | grep -ie [j]nlp | awk '{print $2}' | xargs kill -9					
