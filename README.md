# Lab 2 - Provisioning EC2 Virtual Machine

### What is EC2?
- Amazon Elastic Cloud compute AKA Amazon EC2.
- It is a web service that provides secure resizable compute capacity in the cloud.
- It's designed to make web scale cloud computing easier for developer.


### What will this lab provide?
- First create a single EC2 VM
    - We will scale that out to a vm per availability zone in your region and add a load balancer to spread load balancer across the entire fleet.
- We wouldn't want different links for each of these availability zones so we introduce load balancer which can distribute the load evenly and we will just have a single url to go to and it will determine which server to grab the data from.
    - To handle a lot of people going to the website at once.
    - Load from wherever the load is the lowest


#### Pulumi to create EC2
`pulumi new aws-python -y`



# Lab 3 - Deploying Docker Image to ECS with fargate

AWS Fargate is a service that enables a user to run containers on amazon's cloud computing platform, without the need to manage the underlying infrastructure.

In order to create a fargate service we'll need to add an iam role and a task definition and service. 
The ecs cluster will run the nginx image from the docker hub.