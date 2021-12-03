## Enablement Friday

Hi guys!

Thomas put me in the driving seat for our enablement on Friday.

I'll give you a minute to let that sink in...

Meanwhile, let me take the opportunity to thank you for the past 5 months:

As you might know I ran my own tiny business prior joining DataRobot and this is literally my first permanent role ever. As such it took some getting used to it all - and still does. And while I had and still do have moments questioning this choice in life, you all helped ease that pain significantly. Not least Thomas in our 1/1s.

So thanks to all of you!

What school of thought/management it was that made the very same Thomas decide to have the least knowledgeable guy in the team conduct a team training, has not yet fully transpired.

On the upside, it should be a short Friday. So let's get started:

You'll need

- your workstation
- Internet access
- files from https://github.com/floriankessler/enablementFriday
- docker running
- access to our SaaS

The format of the enablement will be challenge / hint / solution.

On Friday

- at 0900 we'll kick it off. For that I'll update the repo's `README.md` on Friday with the challenges and walk you through it.

  - Task 1 - Name model types and deployment options
  - Task 2 - Create and store a model locally
  - Task 3 - Predict locally using the previously generated model
  - Task 4 - Monitor the model with DR MLOps
    - 4.1 Create and deploy a new Model Package in DataRobot.
    - 4.2 Build a docker image containing the monitoring agent
    - 4.3 Create spooler (rabbitmq)
    - 4.4 Adapt the agent's config to use rabbitmq
    - 4.5 Run the agent within docker using your config
    - 4.6 Instrument and monitor the app

  For hints feel free to ping me everytime. Should it be relevant for the team, I'll create/update `Hints.md` in the repo and inform you on #emea-ai-delivery-private.

- at 1200 we'll reconvene to see how things are going.
- at 1430 we'll have a look at the solutions.

Looking forward to it!
Florian


### Task 1 - Name model types and deployment options

DataRobot knows of three types of models, "external" being only one of them.

- Name them (Bonus points for synonyms)
- List deployment options for all (Bonus points for being detailed about differences)
- What's the MLOps sales pitch across all of them?

### Task 2 - Create and store a model locally

Run `model.py` to create the model's pkl. Use `Dockerfile` as starting point.

### Task 3 - Predict locally using the previously generated model

Create a docker image called `enablement-app:app` containing `app.py`.
Start that image and come up with a prediction using curl.

For that

- augment `Dockerfile` to
  - copy the app as well as the model into the image (`COPY`)
  - start the app (`CMD`)
- have a look into `app.py` to see what a prediction request must look like

### Task 4 - Monitor the model with DR MLOps

Use the MLOps monitoring agent to monitor the model inside a docker container. Use rabbitmq as spooler.

Keep this flow in mind: DR <---> Monitoring Agent <---> Spooler <---> Instrumented app

#### 4.1 Create and deploy a new Model Package in DataRobot.

https://docs.datarobot.com/en/docs/mlops/deployment/registry/reg-create.html#create-model-packages
Remember to pick the correct Prediction type based on what you see on `model.py`

#### 4.2 Build a docker image containing the monitoring agent

Download and extract DataRobot's Monitoring Agent tar file. This is available through the DataRobot MLOps UI via User icon | Developer Tools | External Monitoring Agent.

Build a docker image containing the monitoring agent itself as well as the agent's default config.

See `datarobot_mlops_package-7.3.5/tools/agent_docker/README.md`

#### 4.3 Create spooler (rabbitmq)

https://hub.docker.com/_/rabbitmq

#### 4.4 Adapt the agent's config to use rabbitmq

#### 4.5 Run the agent within docker using your config

See `datarobot_mlops_package-7.3.5/tools/agent_docker/README.md`

#### 4.6 Instrument and monitor the app

Or not! Start with the already instrumented `app-instrumented.py` and make it work, so that you see your queries logged in DR.
Create a new container `enablement-app:instrumented` that comes with all requirements added by the instrumention satisfied.
