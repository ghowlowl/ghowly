# before we do anything we need python, *nix, bash etcetra
# Require:
#  - python pip
#  - python virtualenv

#Change these variable to where all files will go
#default install is under your homedir ~/gautam.92409234 etc

ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_BLUE=$ESC_SEQ"34;01m"
COL_MAGENTA=$ESC_SEQ"35;01m"
COL_CYAN=$ESC_SEQ"36;01m"

red(){ echo -e "${COL_RED}$@${COL_RESET}";}
green(){ echo -e "${COL_GREEN}$@${COL_RESET}";}
yellow(){ echo -e "${COL_YELLOW}$@${COL_RESET}";}
blue(){ echo -e "${COL_BLUE}$@${COL_RESET}";}
magenta(){ echo -e "${COL_MAGENTA}$@${COL_RESET}";}
cyan(){ echo -e "${COL_CYAN}$@${COL_RESET}";}


HOOT_NEST=~/gautam.$(date +%s)
HOOT_EGG_URL=https://github.com/ghowlowl/ghowly.git

#Changes these to your own credentials
AWS_ACCESS_KEY_ID=ccc
AWS_SECRET_ACCESS_KEY=ddd


# --- work begins here ---
export HOOT_NEST
echo "Making nest directory where all owl eggs (ansible playbooks) will go"
mkdir $HOOT_NEST
virtualenv $HOOT_NEST
cd $HOOT_NEST && . bin/activate

#installing ansible 1.3.[1-*]
(
    mkdir tmp && cd tmp
    wget https://github.com/ansible/ansible/archive/v1.3.1.zip
    pip install v1.3.1.zip
    echo "Installed ansible!"
)


#installing ansible 1.3.[1-*]
(
    pip install boto
    pip install awscli
    echo "Installed aws related stuff (boto, awscli)"
)

#is this really needed ahemm
(
    pip install MySQL-python
    pip install termcolor
    echo "Installed mysql-python & termcolor too ;-)"
)

#download playbooks
(

    cd $HOOT_NEST/tmp
    git clone $HOOT_EGG_URL
    mv ghowly* ../ansible
    cd ../ansible
)

#create a setup_env file should be souced for ansible stuff
cd $HOOT_NEST/ansible
setup_env=${HOOT_NEST}/ansible/setup_env
echo export HOOT_NEST=$HOOT_NEST > $setup_env
echo export ANSIBLE_PYTHON_INTERPRETER=$(which python) >> $setup_env
echo export ANSIBLE_HOSTS=${HOOT_NEST}/ansible/inventory/ec2.py >> $setup_env
echo export AWS_CONFIG_FILE=${HOOT_NEST}/ansible/aws/aws.config >> $setup_env

. $setup_env

python ./setup.py

#add sshagent keypair
eval `ssh-agent`
for f in $(ls keys); do
    echo adding $f && chmod 0600 keys/$f && ssh-add keys/$f;
done

##
echo "Setting up two webservers..."
read -p "Press key  to continue... " -n1 -s

ansible-playbook -vvv -i inventory/local.hosts init.yml \
                --extra-vars "host_env=dev host_count=2 host_role=web"


##
echo "Setting up one database ..."
read -p "Press key  to continue... " -n1 -s

ansible-playbook -vvv -i inventory/local.hosts init.yml \
                --extra-vars "host_env=dev host_count=1 host_role=db"

##
echo "Cleaning ec2.py cache..."
read -p "Press key  to continue... " -n1 -s

inventory/ec2.py --refresh-cache --list


##
echo "Install OS and stuff"
read -p "Press key  to continue... " -n1 -s

ansible-playbook -vvv -i inventory/ecs.py site.xml


##
echo "Install app and db"
read -p "Press key  to continue... " -n1 -s

ansible-playbook -vvv -i inventory/ecs.py app.xml


