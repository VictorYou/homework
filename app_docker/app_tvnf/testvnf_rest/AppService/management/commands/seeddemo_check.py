from django.core.management.base import BaseCommand

from TvnfService.models import Tvnf
import sys
sys.path.append("..")
import requests
import json

class Command(BaseCommand):
  help = 'Generates demo data in the database'

  def handle(self, *args, **options):
#    self.create_objects()
    self.check_objects()
#    self.fill_deployment_viminfo_deployconfig()
#    self.register_tvnf()

  def check_objects(self):      
    tvnflist = Tvnf.objects.all()
    print("tvnf list len: {}".format(len(tvnflist)))
    for tvnf in tvnflist:
      print("tvnfId: {}".format(tvnf.tvnfId))

    tclist = Testcase.objects.all()
    print("testcase list len: {}".format(len(tclist)))

  def create_objects(self):
    Tvnf.objects.create(tvnfId='1', tvnfStatus='A')

  def register_tvnf(self):  
    newTvnf = dict(
      accessPoint='10.76.141.149:8000',
      version='0.0.120',
      vnfType='fp-tvnf'
    )
    client = JsonClient()
    response = client.post('/ndap/v1/testvnfs', data=newTvnf)
    print(response.status_code)

  def fill_deployment_viminfo_deployconfig(self):
    vim_info = VimInfo.objects.create(
      domain='demo domain',
      project='v12377_NetAct18A',
      user_name='v12377_viyou',
      dashboard_link='https://10.4.165.38:13000/v2.0', name='My Vlab')
    product = Product.objects.create(
      repository="NetAct",
      name="Deployed NetAct",
      display_name="Deployed NetAct"
    )
    version_1 = product.version_set.create(
      path="19.0",
      name="19.0.9-321-576a0c4",
      value="0000000018-0000000000-0000000019-0000000321"
    )
    user = User.objects.get(username='admin')
    deploy_config_1 = DeployConfig.objects.create(
      file_name="demo_file.zip",
      uploaded_by=user,
      uploaded_at=datetime.now(),
      version=version_1
    )
    Deployment.objects.create(
      deployment_name='1 Succ Dep conf1 vim1',
      state='SUCCESS',
      deploy_config=deploy_config_1,
      target_cloud=vim_info
    )

