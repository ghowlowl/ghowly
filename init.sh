# before we do anything let me tell you there are requirements for it to run
# requirements:
#  - python pip
#  - python virtualenv
#  - ssh-agent
#  - bash
#  - *nix
#  - sense of humor


# Step 1:
# Creates a directory "gautam.$(date +%s)" under your home-dir
# and creates a python virtualenv, into which we installs
# ansible, boto, awscli and other funny python packages...
# Once python virtualenv is all set, we will git clone the repo which has the
# ansible playbook.

# Step 2:
# if all goes well, we runs python ./setup.py which basically asks you
# bunch of question, like AWS_ACCESS_KEY/SECRET_ACCESS_KEY, database
# username/pass... using the info we run aws cli cloudformation for creating
# the VPC, keypairs..
# Later we run few aws cli commands to add these resource ids E.g. vpc id,
# subnet-id etcetra to ansible playbook's variable files

# Step 3:
# Now we are ready to use ansible perfectly... so set up ssh agent,
# add key pairs from step 2..
#   - create ec2 instances:
#       # run ansible init.yml playbook
#   - install base packages,
#       # run ansible site.yml playbook
#   - install web/db packages and app
#       # run ansible app.yml playbook

## Change below 2 vars if you want

HOOT_NEST=~/gautam.$(date +%s)
HOOT_EGG_URL=https://github.com/ghowlowl/ghowly.git
HOOT_BRANCH="blaypook"


## -- code --
ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_BLUE=$ESC_SEQ"34;01m"
COL_MAGENTA=$ESC_SEQ"35;01m"
COL_CYAN=$ESC_SEQ"36;01m"
_ANY_ERROR="NO"

red(){ echo -e "${COL_RED}$@${COL_RESET}";}
green(){ echo -e "${COL_GREEN}$@${COL_RESET}";}
yellow(){ echo -e "${COL_YELLOW}$@${COL_RESET}";}
blue(){ echo -e "${COL_BLUE}$@${COL_RESET}";}
magenta(){ echo -e "${COL_MAGENTA}$@${COL_RESET}";}
cyan(){ echo -e "${COL_CYAN}$@${COL_RESET}";}

## -- code --
yell() { echo -e "${COL_RESET}${COL_YELLOW}";}
si() {
    is "bad" $@
}

is() {
    local _now=$(date +%Y-%m-%d\ %H:%M:%S)
    local _is=$1
    shift
    echo -e $COL_RESET
    if [[ "${_is}" == "good" ]]; then
        _ANY_ERROR="NO"
        [[ $# > 0 ]] && green $now $@ || green $now "All good"
        return 0;
    elif [[ "${_is}" == "bad" ]]; then
        _ANY_ERROR="YES"
        [[ $# > 0 ]] && red $now $@ || red $now "did something break somewhere?"
        return 1
    else
        [[ ${_ANY_ERROR} == "NO" ]] && green $now ${_is:-"All ok, continuing"} $@ && return 0;
        red $now "ERROR:" ${_is:-""} $@ && return 1;
    fi
}



# --- work begins here ---
export HOOT_NEST


##
MSG="Making nest directory where all owl eggs (ansible playbooks) will go"
ERR="Making nest directory where all owl eggs (ansible playbooks) will go"
is $MSG && \
(
    yell
    mkdir $HOOT_NEST && virtualenv $HOOT_NEST
) || si $ERR


##
MSG="Activating virtualenv"
ERR="Failed activating virutalen"
is $MSG && yell && cd $HOOT_NEST && . bin/activate || si $ERR


##
MSG="Making nest directory where all owl eggs (ansible playbooks) will go"
ERR="Failed activating virutalen"
is $MSG && \
(
    yell
    mkdir tmp \
    && cd tmp \
    && wget https://github.com/ansible/ansible/archive/v1.3.1.zip  \
    && pip install v1.3.1.zip
) || si $ERR


##
MSG="Installing boto, awscli, mysql-python, termcolor"
ERR="Failed pip installs.."
is $MSG && \
(
    yell
    pip install boto \
    && pip install awscli \
    && pip install MySQL-python \
    && pip install termcolor
) || si $ERR


#download playbooks
MSG="Git clone $HOOT_EGG_URL"
ERR="Failied cloning repos! OMG!"
is $MSG && \
(
    yell
    cd $HOOT_NEST/tmp \
    && (
        [[ $HOOT_BRANCH ]] && git clone -b $HOOT_BRANCH $HOOT_EGG_URL \
        || git clone $HOOT_EGG_URL
        ) \
    && mv ghowly* ../ansible \
    && cd ../ansible \
) || si $ERR


#create a setup_env file should be souced for ansible stuff
setup_env=${HOOT_NEST}/ansible/setup_env && export setup_env
MSG="Creating $setup_env file with ANSIBLE's env vars, (it should be srced)"
ERR="An epic fail! sum ting wong! Bail out naaawww"
is $MSG && \
(
    yell
    set +o noclobber
    echo ". $HOOT_NEST/bin/activate" > $setup_env
    echo export HOOT_NEST=$HOOT_NEST >> $setup_env
    echo export ANSIBLE_PYTHON_INTERPRETER=$(which python) >> $setup_env
    echo export ANSIBLE_HOSTS=${HOOT_NEST}/ansible/inventory/ec2.py >> $setup_env
    echo export AWS_CONFIG_FILE=${HOOT_NEST}/ansible/aws/aws.config >> $setup_env
) || si $ERR


clear
is "sourcing $setup_env file..." && . $setup_env || si "Unable to src $setup_env"


clear
is "executing setup.py file..." \
    && cd $HOOT_NEST/ansible \
    && (python ./setup.py) \
    || si "some error setting up using setup.py"
wait


clear
is "starting ssh-agent..." && {
    eval `ssh-agent`
    for f in $(ls keys); do
        green adding $f to ssh-agent && chmod 0600 keys/$f && ssh-add keys/$f;
    done
}


##
is && {

    clear
    green  "Automated install using ansible.. you can sit back and relax now.."
    green  " you can go and drink some latte/cappucino/mocha or ipa/stout/lager.."
    read -p "Press key to continue... " -n1 -s

    clear
    green "Setting up 2 webservers..."
    #read -p "Press key to continue... " -n1 -s
    ansible-playbook -vvv -i inventory/local.hosts init.yml \
                    --extra-vars "host_env=dev host_count=2 host_role=web"


    ##
    clear
    green "Setting up 1 database ..."
    #read -p "Press key to continue... " -n1 -s
    ansible-playbook -vvv -i inventory/local.hosts init.yml \
                    --extra-vars "host_env=dev host_count=1 host_role=db"

    ##
    clear
    #green "Clean ec2.py cache..."
    read -p "Press key to continue... " -n1 -s
    inventory/ec2.py --refresh-cache --list


    ##
    clear
    green "Install OS and stuff"
    #read -p "Press key to continue... " -n1 -s
    ansible-playbook -vvv site.yml


    ##
    clear
    green "Install app and db"
    #read -p "Press key to continue... " -n1 -s
    ansible-playbook -vvv app.yml

    clear
    green "All done, test using loadbalancer/inctance ip"

} || {
    echo "Blame Canda!"
}
