


LAMP on 3 ec2 instances in VPC
================================================================
#### Uses 2 instances as webservers and 1 instance as database and 1 ELB. The webserver, database hosts and load-balancer are in there own security group - allowing finer security control. The hosts are 64bit Ubuntu precise and webservers use Apache2 + PHP and db is MySQL. Latest wordpress is installed. Go have fun!


To test:
--------------------
    1. Goto /tmp dir
        - $ cd /tmp/
    2. Download init.sh from either URLs
        - #master branch
            - $ wget https://raw.github.com/ghowlowl/ghowly/master/init.sh
    3. source init.sh
        - $ . init.sh
        # init.sh should do the rest and create a python virtual env
        # in your homedir  ~/gautam.*/
        # I wrote this on Mac OS X, bash and python 2.7...


Let me explain first.
--------------------

    1. I have used aws-cli, ansible & cloudformation. The playbooks are
       designed to be flexible to create dev|prod|stage env in their own VPC
       and for added security ec2 instances are addeed into their own security
       group. This also uses Elastic IPs

    2. ./setup.py - Initial setup by private VPC
        - Asks which env dev|prod
        - Asks which region
        - Asks MySql info for db
        - Uses Cloudformation
            - VPC
            - Subnet
            - ROute Table
            - DHCP Opts
            - ACLs
            - Security Group
            -  Internet GW
            - and associating them...
        - Read resource id variables to ansible var yml files using jinja
        - AWS CLI: generate keypair and add download it.

    3. An ansible playbook_runner.sh is created by step 2, it basically
       executes ansiblle playbooks in following order:

        3.1 init.yml - when VPC is ready, we fire up ansible to do initial setup for
            - creating EC2 instances
            - assign role tags "db" or "web" and "dev" or "prod"
            - create Elastic IPs for each
            - create security group depending on role
                - add ingress/egress traffic rules
                - enable 80/22 port
            - if web creating ELB, add listners
            ansible- refresh ./ec2.py inventory cache

        3.2 site.xml -
            - installs base packages
            - assign roles:
                - install db packages
                - install httpd php packages

        3.3 app.xml - deploy apps and add mysql account for the apps
            - Web app
                - add own index.php remove index.html
                - downloads wordpress/latest.tar.gz
                - installs it in /var/www
                - adds db pvt ip to /etc/hosts
                - adds mysql db account details into php-config
            - DB app
                - creates app specific database
                - creates app user acct and grants priv
                - modifies /etc/mysql/conf.d to enable listen on 0.0.0.0
                - restart mysql service

        3.4. To test we use  loadbalancers ip, you will see index.php
             go to http://loadbalancer.ip.amazon/blog/ it will launch
             wordpress blog. We are all good if you see it.

    4. Later if you ever wish to run ansible commands or aws cli on your own
        - source setup_env file
            . $HOOT_NEST/ansible/setup_env
        - run your ansible commands/aws cli commands


Conclusion
--------------------
I know it could be a lot simpler by just doing everything with cloudformation, but I used that at minimum. I started off using trying everything with ansible, then used aws cli where it was not possible. And realised creating private VPC was complicated with too many resources so I ended up using cloudformation. Anyways learnt a great deal!!

Beta branch
--------------------
    - the latest/testing code is in "blaypook branch"
    - run 'wget https://raw.github.com/ghowlowl/ghowly/blaypook/init.sh'
    - edit init.sh to ensure HOOT_BRANCH is uncommented and uses the blaypook branch
