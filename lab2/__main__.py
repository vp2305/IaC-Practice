"""An AWS Python Pulumi program"""
# pulumi new aws-python -y
import pulumi
import pulumi_aws as aws

"""
Notes:

Amazon machine image that provides information required to launch an instance

We are going add multiple ec2 instances. 
We're going to create multiple instances that are each running the same python web server and we're going to make them across all aws availability zones in the region.

We wouldn't want different links for each of these availability zones so we introduce load balancer which can distribute the load evenly and we will just have a single url to go to and it will determine which server to grab the data from.
    - To handle a lot of people going to the website at once.
    - Load from wherever the load is the lowest
"""

# get the ami with code
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["137112412989"],  # Set the owner of the ami
    filters=[
        {"name": "name", "values": ["amzn-ami-hvm-*-x86_64-ebs"]}
    ],  # Filters we have to use
)

# Service that allows to let you launch aws resources in a logically isolated virtual network that you define. (Available in our aws account)
vpc = aws.ec2.get_vpc(default=True)


# AWS Security Group which will enable ping over icmp and http traffic on port 80
group = aws.ec2.SecurityGroup(
    "web-secgrp",
    description="Enable HTTP access",
    ingress=[
        {
            "protocol": "icmp",
            "from_port": 8,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    # Need to add egress rule to the security group. Whenever you add a listener to your load balancer or update the health check port for a target group used by the load balancer to route requests.
    # You must verify that the security group associated with the load balancer allow traffic to the new port in both direction.
    # So that this rule don't conflict with the load balancer.
    egress=[
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
)

"""
Start of Load balancer creation
"""

# Subnet of the vpc
vpc_subnets = aws.ec2.get_subnet_ids(vpc_id=vpc.id)

# Create a load balancer
lb = aws.lb.LoadBalancer(
    "loadbalancer",
    internal=False,  # So it can be accessed by the public
    security_groups=[group.id],
    subnets=vpc_subnets.ids,
    load_balancer_type="application",
)


target_group = aws.lb.TargetGroup(
    "target-group",
    port=80,
    protocol="HTTP",
    target_type="ip",
    vpc_id=vpc.id,
)

listener = aws.lb.Listener(
    "listner",
    load_balancer_arn=lb.arn,
    port=80,
    default_actions=[
        {
            "type": "forward",
            "target_group_arn": target_group.arn,
        }
    ],
)

"""
End of load balancer creation
"""


# New IP and hostname for each aws availability zone
ips = []
hostnames = []

for az in aws.get_availability_zones().names:
    # Create a server that spits up a python starter code.
    server = aws.ec2.Instance(
        f"web-server-{az}",
        instance_type="t2.micro",  # Types of different server you can create
        # vpc_security_group_ids=[group.id],  # Ids from the security group
        security_groups=[group.name],
        ami=ami.id,  # Id from the ami
        availability_zone=az,
        # In real world example we would want to create a dedicated image for your application rather than embedding the script in the code like this.
        user_data=""" 
            #!/bin/bash
            echo \"Hello, World! -- from {}\" > index.html
            nohup python -m SimpleHTTPServer 80 &
        """.format(
            az
        ),
        tags={"Name": "web-server"},
    )

    ips.append(server.public_ip)
    hostnames.append(server.public_dns)

    # Attach the server to the Amazon Load Balancer
    attachment = aws.lb.TargetGroupAttachment(
        f"web-server-{az}",
        target_group_arn=target_group.arn,
        target_id=server.private_ip,
        port=80,
    )


pulumi.export("ips", ips)
pulumi.export("hostnames", hostnames)
pulumi.export("url", lb.dns_name)
