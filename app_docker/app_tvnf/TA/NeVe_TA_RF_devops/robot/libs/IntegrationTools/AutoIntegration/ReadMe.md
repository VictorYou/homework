# Integration Tool

## Introduction:
>This tool support to integrate SBTS, OMS, BSC to NetAct, include creating credential and MR,MRC Object 
>This tool use Nasda API to create MR, MRC Object, CredTestTool to create credentials and via NEIW to integrate NE to NetAct. 
 
## Release:
    V1.00:
        1.Initialize version.

***
## Usage:
### 1.Name:
    Integration Tool
    
### 2. Steps:
    a.Modify the integration parameters in scripts(AutoIntegration_BSC.py, AutoIntegration_OMS.py, AutoIntegration_SBTS.py). Those parameters are located in the botom of those python script file.
    b.Run the integration script.
    c.Waiting for the integration operation done.
    
### 4. Environment:  
    a.Please add the oss_radio_tools_lib to your python path.
    b.Please add the oss_radio_tools_lib/NetAct or add the adaptation common TA lib to your python path.
    
### 4. LOG:
    The operation log will be saved to AutoIntegration_XXX.log(AutoIntegration_BSC.log,AutoIntegration_OMS.log,AutoIntegration_SBTS.log) file in your work directory.
    