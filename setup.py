#!/usr/bin/env python


import os
import sys
from termcolor import colored
import jinja2
import subprocess, threading
import tempfile
import re
import time
import json

test = None
if test:
    env = "dev"
    region = "us-west-1"
    access_key = "AKIAJRX3QJDEN75JTCTA"
    secret_key = "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"
    dbname = "owly"
    dbuser = "owly"
    dbpass = "owly"

#delete this before you die
tmpdir = tempfile.mkdtemp(prefix='tmp')

#simple classs to execute cmd in a thread, tee output and return it.
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.outfile = tmpdir + '/out'
        self.out = ''

    def run(self, timeout=1200):
        def target():
            print '>>> Thread executing '
            print '>>> executing ' + self.cmd
            self.process = subprocess.Popen("(" + self.cmd + ") |tee " + self.outfile, shell=True)
            self.process.communicate()
            print '>>> Thread done'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print '>>> Thread timed out {} seconds'.format(timeout)
            print '>>> Thread terminating process'
            self.process.terminate()
            thread.join()
        try:
            with open (self.outfile, "r") as myfile:
                self.out=myfile.read()
        except:
            self.out=''
        return self.process.returncode, self.out

#jinja2 writer
def writerender(templater, src, dst, vars):
    template = templater.get_template(src)
    with  open(dst, mode="w") as f:
        f.write(template.render(vars))
    print ">>> jinja2 wrote file '{}".format(dst)

#read input
def myinput(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


#color text output
def green(m):
    return colored(m,'green')


#color text output
def red(m):
    return colored(m,'red')


#print formatted terminal screen
def mypage(step=0, headline="Hello there...", msg="Hoot Hoot! Welcome to the tech challenge's inital setup", ask="Press any key to continue ...", retry=None):
    os.system('cls' if os.name=='nt' else 'clear')
    ask = colored(ask, 'green')
    if retry:
        retry = ">>> {}".format(colored(retry, 'red'))
    else:
        retry = ''
    msg_format1 = """
===============================================================================
{}
===============================================================================

    {}
    {}
    >>> {}
    >>>""".format(
        str.center("(step " + str(step) + ") " + headline, 79),
        retry, msg, ask)
    msg_format2 = """
===============================================================================
{}
===============================================================================

    {}


    {}""".format(
        colored(str.center(headline, 79), 'green'),
        colored(msg, attrs=['bold']), ask)
    #
    if step != 0:
        print(msg_format1),
    else:
        print(msg_format2),
    return myinput("")

###############################################################################
# welcome
###############################################################################
mypage()


###############################################################################
# overview
###############################################################################
msg="""Hello!

  {}
  Before we begin:
    I hope you edited & sourced 'source init.sh', that sets up the python
    VirtualEnv and does a pip install of required ansible packages. It will
    download ansible playbooks needed. If you're good lets proceed then. Else
    vim 'init.sh' and edit it. Then source it as '. init.sh'

  Lets proceed:
    First we setup the inital environments for LAMP infrastructure... There are
    going to be 2 environments one as "dev", another as "prod". These
    infrastructure will run in their "own" VPC and in the regions of your
    choice.

    But before we can proceed we need to answer some questions for our
    environemnts. And then

  Next steps:
    1) Which env? (dev or prod)
    2) Prefered VPC region
    3) Enter AWS credentials
        3.1) AWS key
        3.2) AWS secret
    4) Mysql configure
        4.1) db name
        4.2) db username
        4.3) db password"""
mypage(msg=msg.format(''))
check=1
while check is not None:
    try:
        nest = os.environ['HOOT_NEST']
        os.environ['AWS_CONFIG_FILE']
        os.environ['ANSIBLE_PYTHON_INTERPRETER']
        os.environ['ANSIBLE_HOSTS']
    except:
        mypage(msg=msg.format(red("Cant find environ variable, src init.sh first!")))
    else:
        check = None


"""
print "Where do you want your 'dev' environment VPC"
aws_secret_key = input('Enter the "AWS Region"? ')
mysql_database_name = input('Enter the "AWS Region"? ')
mysql_database_user = input('Enter the "AWS Region"? ')
mysql_database_pass = input('Enter the "AWS Region"? ')

aws_access_key = input('Enter your "AWS_ACCESS_KEY_ID"? ')
aws_secret_key = input('Enter your "AWS SECRET ACCESS KEY"? ')
"""


###############################################################################
# which env
###############################################################################

envs = ["dev", "prod"]

headline = "Configure env"
msg = """So we are going to create separate dev, prod environment and host.
    The environments are going to be in there own VPCs"""
ask = """Select the env you wish to configure? [{}]""".format("|".join(envs))
step = 1
if not test:
    env = mypage(step=step, headline=headline, msg=msg, ask=ask)
    while env not in envs:
        env = mypage(step=step, headline=headline, msg=msg, ask=ask, retry="{} is incorrect choice".format(env))
    mypage(headline=headline, msg="Selected '{}' env".format(env))



###############################################################################
# which region
###############################################################################

regions = ["us-west-1", "us-west-2", "us-east-1", "eu-west-1"]

headline = "Choose region"
msg = """Your '{}' env can be configured in various regions, chose one
    closest to the users""".format(env)
ask = """Select the region you wish to use? [{}]""".format("|".join(regions))
step = 2

if not test:
    region = mypage(step=step, headline=headline, msg=msg, ask=ask)
    while region not in regions:
        region = mypage(step=step, headline=headline, msg=msg, ask=ask, retry="{} is incorrect choice".format(region))
    mypage(headline=headline, msg="Selected '{}' env".format(region))


###############################################################################
# AWS Key
###############################################################################

headline = "Enter your AWS credentials (ACCESS_KEY)"
msg = """Your '{}' env will be created in '{}'! But to connect we
    need to set AWS credentials first. These credentials will be
    saved in:
        $HOOT_NEST/ansible/aws/{}.aws.config
        $HOOT_NEST/ansible/vars/common.yml
    The aws cli and ansible playbooks will read these files.""".format(env, region, env)
ask = """Enter your AWS_ACCESS_KEY_ID"""
step = 3.1

if not test:
    access_key = mypage(step=step, headline=headline, msg=msg, ask=ask)

###############################################################################
# AWS Secret
###############################################################################

headline = "Enter your AWS credentials (SECRET_KEY)"
ask = """Enter your AWS_SECRET_ACCESS_KEY_ID"""
step = 3.2

if not test:
    secret_key = mypage(step=step, headline=headline, msg=msg, ask=ask)
    mypage(headline=headline, msg="ACCESS_KEY is {}\n    SECRET_KEY is {}".format(access_key, secret_key))


###############################################################################
# DB Name
###############################################################################

headline = "Configure mysql db "
msg = """Add details about the you '{}' mysql db. The webapp will connect to
    this mysql db instance. These enteries will be added to ansible var files
    saved in:
        $HOOT_NEST/ansible/vars/{}/db/common.yml
        $HOOT_NEST/ansible/vars/{}/web/common.yml
    You may edit those files later""".format(env, env, env)
ask = """Enter db name? /[a-z0-9]+/"""
step = 4.1
if not test:
    dbname = mypage(step=step, headline=headline, msg=msg, ask=ask)


###############################################################################
# DB User
###############################################################################

headline = "Configure mysql db "
msg = """Add details about the you '{}' mysql db. The webapp will connect to
    this mysql db instance. These enteries will be added to ansible var files
    saved in:
        $HOOT_NEST/ansible/vars/{}/db/common.yml
        $HOOT_NEST/ansible/vars/{}/web/common.yml
    You may edit those files later""".format(env, env, env)
ask = """Enter user for database '{}'? """.format(dbname)
step = 4.1
if not test:
    dbuser = mypage(step=step, headline=headline, msg=msg, ask=ask)


###############################################################################
# DB Pass
###############################################################################


headline = "Configure mysql db "
msg = """Add details about the you '{}' mysql db. The webapp will connect to
    this mysql db instance. These enteries will be added to ansible var files
    saved in:
        $HOOT_NEST/ansible/vars/{}/db/common.yml
        $HOOT_NEST/ansible/vars/{}/web/common.yml
    You may edit those files later""".format(env, env, env)
ask = """Enter password for user '{}'? """.format(dbuser)
step = 4.1
if not test:
    dbpass = mypage(step=step, headline=headline, msg=msg, ask=ask)
    _ = mypage(headline=headline, msg="dbname is {}\n    dbuser is {}\n    dbpass is {}".format(dbname, dbuser, dbpass))

###############################################################################
###############################################################################


ansible_dir =  os.environ.get('HOOT_NEST') + "/ansible"
templater = jinja2.Environment(
      loader = jinja2.FileSystemLoader( ansible_dir + "/setup/" )
      )


vars = {
    "access_key": access_key,
    "secret_key": secret_key,
    "region": region,
    "env": env,
    "dbname": dbname,
    "dbuser": dbuser,
    "dbpass": dbpass,
    }

writerender(templater, 'aws.config.j2', os.environ.get("AWS_CONFIG_FILE"), vars)

session_id = str(int(time.time()))[-5:]


###############################################################################
###############################################################################

mypage(
    headline="Starting aws cloudformation setup",
    msg="""Going to setup:
        - VPC
        - Subnet
        - Internet Gateway
        - Routing Table
        - DHCP Options
        - VPC Security Group
        - Gateway
        - ACL
    Using cloudformation template {}
    """.format(ansible_dir + '/setup/cloudformation.template.json'))

stack_name = "ass123"
#stack_name = "tmp" + session_id

# '''
stack_create_cmd = 'aws cloudformation create-stack --stack-name {} --template-body file://setup/cloudformation.template.json --region {} --output text'.format(stack_name, region)
stack_create = Command(stack_create_cmd)
retval, stack_id = stack_create.run()
create_finish = None

if re.match('.*cloudformation.*', stack_id):
    stack_checker_cmd = """aws cloudformation list-stacks --region {} --output text | grep {} | awk '{{print $NF}}'""".format(region, stack_name)
    stack_checker = Command(stack_checker_cmd)
    retval, create_status = stack_checker.run()
    while re.match('.*CREATE_COMPLETE', create_status) is None:
        print "Stack creation not complete, waiting..."
        time.sleep(10)
        retval, create_status = stack_checker.run()
    print "Stack creation complete"
else:
    print "Stack creation exception"
    sys.exit(1)
# '''

stack_desc_cmd = 'aws cloudformation describe-stack-resources --stack-name {} --region {}'.format(stack_name, region)
stack_desc = Command(stack_desc_cmd)
_, stack_desc_out = stack_desc.run()

try:
    data = json.loads(stack_desc_out)
    for res in data['StackResources']:
        res_id =  res['PhysicalResourceId']
        if re.match('vpc-.*', res_id):
            vars['vpc_id'] = res_id

        if re.match('igw-.*', res_id):
            vars['igw_id'] = res_id

        if re.match('rtb-.*', res_id):
            vars['routetbl_id'] = res_id

        if re.match('subnet-.*', res_id):
            vars['subnet_id'] = res_id

        if re.match('sg.*', res_id):
            vars['sg_id'] = res_id
except Exception, e:
    print "Stack data parsing failed", e

###############################################################################
# ssh
###############################################################################

sg_fetch = Command(
    """aws ec2 describe-security-groups --output text --region {} | grep {} | awk '{{print $NF}}'""".format(region, vars['vpc_id'])
    )
_, sg_out = sg_fetch.run()

if sg_out and re.match('.*sg-.*', sg_out):
    vars['sg_id'] = sg_out
else:
    print "Exception parsing Security group"
    sys.exit(1)

###############################################################################
# keypair
###############################################################################

kp = stack_name + "kp"
vars['keypair'] = kp
mypage(
    headline="Create key pairs",
    msg="""Let's generate keypairs for {env} env, we will exclusively use it to
    connect to out EC2 instances, the ssh -keys will be stored in
        - {nest}/ansible/keys/{env}_{kp}.rsa
    Ensure the keys are added to your ssh-agent!""".format(
        nest=nest, env=env, kp=kp))

key_cmd = "aws ec2 create-key-pair --key-name '{}' --region {}".format(kp, region)
key_create = Command(key_cmd)
_, key_out =key_create.run()


try:
    data = json.loads(key_out)
    vars['key'] = data['KeyMaterial']
except Exception, e:
    print "Key data parsing failed", e
else:
    writerender(templater, 'ssh.j2',
        '{nest}/ansible/keys/{env}_{kp}'.format(
            nest=nest,
            env=env,
            kp=kp
            ),
        vars)


###############################################################################
# ami
###############################################################################

ami = {}
ami['us-west-1'] = "ami-fe002cbb"
ami['us-west-2'] = "ami-70f96e40"
ami['us-east-1'] = "ami-d0f89fb9"
ami['eu-west-1'] = "ami-ce7b6fba"
vars['ami_id'] = ami[region]


###############################################################################
# yamls
###############################################################################

mypage(
    headline="Adding resouces ids to ansible vars",
    msg="""Cloudformation has completed creating basic VPC infrastructure,
    the resouces-ids will be added to ansible vars..
        - {nest}/ansible/vars/common.yml
        - {nest}/ansible/vars/{env}/common.yml
        - {nest}/ansible/vars/{env}/web/common.yml
        - {nest}/ansible/vars/{env}/db/common.yml"""
        .format(
            nest=nest,
            env=env
            )
        )
vars['py_interpreter'] = str(sys.executable)

files = [
    {
        'dst': '{nest}/ansible/vars/common.yml'.format(
            nest=nest),
        'src': 'vars_common.yml.j2'
    },
    {
        'dst': '{nest}/ansible/vars/{env}/common.yml'.format(
            nest=nest,
            env=env),
        'src': 'vars_@env_common.yml.j2'
    },
    {
        'dst': '{nest}/ansible/vars/{env}/roles/db/common.yml'.format(
            nest=nest,
            env=env),
        'src': 'vars_@env_roles_@role_common.yml.j2'
    },
    {
        'dst': '{nest}/ansible/vars/{env}/roles/web/common.yml'.format(
            nest=nest,
            env=env),
        'src': 'vars_@env_roles_@role_common.yml.j2'
    },
    {
        'dst': '{nest}/ansible/inventory/local.hosts'.format(
            nest=nest),
        'src': 'local.hosts.j2'
    },
]

for pair in files:
    writerender(templater, pair['src'], pair['dst'], vars)


mypage(
    headline="All done",
    msg="""Now we can begun setting up the env using ansible!!
        - EC2 create 2 web instances...
            ' ansible-playbook -vvv -i inventory/local.hosts init.yml
                --extra-vars "host_env={env} host_count=1 host_role=db" '

        - EC2 create 1 db web instances...
           ' ansible-playbook -vvv -i inventory/local.hosts initial.yml
                --extra-vars "host_env={env} host_count=1 host_role=db" '

        - Deploy OS and other configs
            ' ansible-play'
        - {nest}/ansible/vars/{env}/common.yml
        - {nest}/ansible/vars/{env}/web/common.yml
        - {nest}/ansible/vars/{env}/db/common.yml"""
        .format(
            nest=nest,
            env=env
            )
        )
print("bye")
