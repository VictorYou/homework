#!/bin/bash
rm -rf NeVe_TA_RF NeVe_TA_RF.zip
git clone ssh://viyou@gerrite1.ext.net.nokia.com:8282/NeVe_TA_RF
cd NeVe_TA_RF \
&& git branch current_master origin/master \
&& git checkout current_master \
&& rm -rf .git \
&& cd -
rm -rf NeVe_TA_RF/robot/tests/VSs/
for file in NeVe_TA_RF/robot/tests/level6/*; do
  if [ `grep MRBTS $file | wc -l` -eq 0 ]; then
    filename=$(basename $file)
    if [ $filename != 'tc_reg_COMMON_Administration_suite.robot' ]; then
      rm -rf $file
    fi
  fi
done

find NeVe_TA_RF/robot/tests/level6/ -type f -iname "*Mediator*.robot" -exec rm -rf {} \;
find NeVe_TA_RF/robot/tests/level6/ -type f -iname "*Subtype*.robot" -exec rm -rf {} \;

find NeVe_TA_RF_devops -type f -exec dos2unix {} \;

sed -ri 's|(export PYTHONPATH=.*)|\1/home/$USER/robot/libs/oss_radio_tools_lib/NetAct/:/home/$USER/robot/libs/oss_radio_tools_lib/Remote/:|' NeVe_TA_RF/robot/xubuntu_executor.sh
sed -ri 's/^(\$\{scope\}          ).*$/\1\$\{EDV_MRBTS_MRC_INSTANCE\}/' NeVe_TA_RF/robot/tests/NEs_affecting/tc_reg_LTE_MRBTSFZM_NEIW_integration.robot
sed -ri 's/^(\$\{NE_TYPE\}        ).*$/\1MRBTS/' NeVe_TA_RF/robot/tests/NEs_affecting/tc_reg_LTE_MRBTSFZM_NEIW_integration.robot
sed -ri 's/^(.*\@\{groups\}    Create list    ).*(tagroup)$/\1\2/' NeVe_TA_RF/robot/tests/NEs_affecting/tc_reg_LTE_MRBTSFZM_NEIW_integration.robot
sed -ri 's/(.*\$\{scope\}=.*)/#\1/' NeVe_TA_RF/robot/tests/resources/res_neac.robot

cp -r NeVe_TA_RF_devops/* NeVe_TA_RF/

python3 prepare_elementdatavariables.py NeVe_TA_RF/configuration/nevescripts/ElementDataVariables.xml
python3 prepare_labdata.py NeVe_TA_RF/configuration/nevescripts/LabData.json
