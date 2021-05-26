| *** Settings *** |
| Library        | ../libraries/requests_wrapper.py |
| Variables      | ../libraries/dynamic_vars.py |
| Library        | ../libraries/Testvnf_keywords.py |

| *** Variables *** |
| ${DEPLOYMENTINFO} | add a sut |
| @{list}        | 'viyou' |

| *** Test Cases *** |
| add a sut OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | Should Contain | ${ret} | "result":"OK" |
|    | [Teardown] | Testvnf Teardown |

| add a sut NOK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | Should Contain | ${ret} | "result":"NOK" |
|    | [Teardown] | Testvnf Teardown |

| get testcase OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${response}= | Send Http No Proxy | GET | ${TESTVNF_URL}/suts/${randomsutId} |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "tc list":[1,2,3] |
|    | [Teardown] | Testvnf Teardown |

| get testcase NOK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${nasutid} | Evaluate | ${randomsutId}+1 |
|    | ${response}= | Send Http No Proxy | GET | ${TESTVNF_URL}/suts/${nasutid} |
|    | Should Contain | ${response} | "result":"NOK" |
|    | Should Not Contain | ${response} | "tc list":[1,2,3] |
|    | [Teardown] | Testvnf Teardown |

| run testcase OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${ret}= | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${response}= | Send Http No Proxy | POST | ${TESTVNF_URL}/suts/${randomsutId}/runTests/ | -d testcases=[1,2,3] -d sessionId=12345 -d tvnfId=${randomtvnfId} |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "class":"RunTestcaseReq" |
|    | [Teardown] | Testvnf Teardown |

| remove a sut OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${ret}= | Remove One SUT | ${randomsutId} |
|    | Should Contain | ${ret} | "result":"OK" |
|    | Should Contain | ${ret} | "class":"ResetReq" |
|    | [Teardown] | Testvnf Teardown |

| remove a sut NOK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsutId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${randomtvnfId} | Evaluate | random.randint(0,10000) | modules=random |
|    | Add One SUT | ${randomsutId} | ${randomtvnfId} |
|    | ${nasutId}= | Evaluate | ${randomsutId}+1 |
|    | ${ret}= | Remove One SUT | ${nasutId} |
|    | Should Contain | ${ret} | "result":"NOK" |
|    | [Teardown] | Testvnf Teardown |

| query tvnf status OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${response}= | Send Http No Proxy | GET | ${TESTVNF_URL}/testvnf/v1/status |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "class":"QueryStateReq" |
|    | [Teardown] | Testvnf Teardown |

| abort test execution OK |
|    | [Documentation] | get test case from test vnf |
|    | [Setup] | Testvnf Startup |
|    | ${randomsessionId} | Evaluate | random.randint(0,10000) | modules=random |
|    | ${response}= | Send Http No Proxy | POST | ${TESTVNF_URL}/testvnf/v1/abortTests/${randomsessionId}/ |
|    | Should Contain | ${response} | "result":"OK" |
|    | Should Contain | ${response} | "class":"AbortTestExecutionReq" |
|    | [Teardown] | Testvnf Teardown |

| dummy test |
|    | @{ret}= | Get Service User Types |
|    | log | @{ret} |

| *** Keywords *** |
| Add One SUT |
|    | [Arguments] | ${sutId} | ${tvnfId} |
|    | ${response}= | Send HTTP No Proxy | POST | ${TESTVNF_URL}/suts/ | -d sutId=${sutId} -d tvnfId=${tvnfId} -d deploymentInfo="${DEPLOYMENTINFO}" |
|    | [Return] | ${response} |

| Remove One SUT |
|    | [Arguments] | ${sutId} |
|    | ${response}= | Send HTTP No Proxy | DELETE | ${TESTVNF_URL}/suts/${sutId}/ |
|    | [Return] | ${response} |

| Get Service User Types |
|    | Return from keyword if | True | @{list} |
