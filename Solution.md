## External Models

### Task 1 - Name model types and deployment options

DataRobot knows of three types of models, "external" being only one of them.

- Name them (Bonus points for synonyms)
- List deployment options for all (Bonus points for being detailed about differences)
- What's the MLOps sales pitch across all of them?

---

DR MLOps can    (sales pitch!)

- monitor model performance (monitoring agent) and
- manage model lifecycle (management agent)

of all models. We talk about

- *[native|DR] models* vs
    created 'inside' DR. And are registered automatically as deployment-ready model packages in the model registry.
- *custom models* vs
    created 'outside' DR. But imported into DR via the Custom Model Workshop in the model registry.
- *[external|remote]* models
      neither created nor imported into DR. But still to be monitored (Monitoring Agent) / managed (Management Agent aka Bosun) by DR via [remote|external] model package in the registry.

Deployment options

- for native models are
  - DPE (container magic feeding on `mlpkg`s within a VM) and
  - PPS ( *fat* docker container containing the base for *every* language we support)
  - export as scoring code (well,
    - for ~90% of classification/regression models
    - x% of time series models currently in beta
    - x% of multiclass models
    - not for unsupervised models)
- for custom models are
  - DPE (using a drop-in env placed on K8s sitting behind our DPE-API) and
  - PPS light-ish (*not so fat* docker container containing the base for the language the model in question actually uses as well as the monitoring agent)
- external models are
  - per definitionem unlimited

Aside: The drop-in env can be

- stock
- augmented (eg `requirements.txt`)
- custom (given the rights to upload those envs)

Another aside: We seem to hardwire the API endpoint into our downloads. So an [PPS|agent|...] downloaded from [US SaaS|EU SaaS|customer's install] is only ever usable with that specific

Differences in feature set depending on origin and deployment of models:

- Automatic retraining and humility available only for native models via DPE

### Task 2 - Create and store a model locally

Run `model.py` to create the model's pkl. Use `Dockerfile` as starting point.

#### Solution

```bash
time docker build -t enablement-app:build-model -f Dockerfile .
```

```bash
docker run \
  --rm \
  --name enablement-app \
  --volume ${PWD}:/host \
  --workdir /host \
  -ti \
  enablement-app:build-model \
  bash
    # create the model
    cd model
    python model.py

    # leave the container
    exit
```

### Task 3 - Predict locally using the previously generated model

Create a docker image called `enablement-app:app` containing `app.py`.
Start that image and come up with a prediction using curl.

For that

- augment `Dockerfile` to
  - copy the app as well as the model into the image (`COPY`)
  - start the app (`CMD`)
- have a look into `app.py` to see what a prediction request must look like

#### Solution - Create a docker image

```bash
cat << 'EOF_Dockerfile' > Dockerfile
FROM python:3.7

# Ensure that the python output is sent straight to terminal (e.g. your
# container log) without being first buffered and that you can see the output
# of your application (e.g. flask logs) in real time.
ENV PYTHONUNBUFFERED 1

# Prevent Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/* .
COPY model/* ./model/

EXPOSE 9091
CMD [ "python", "/usr/src/app/app.py", "run" ]
EOF_Dockerfile

docker build -t enablement-app:app -f Dockerfile .
```

```bash
docker run \
  -d \
  --name enablement-app \
  --publish 80:9091 \
  enablement-app:app

docker logs -f enablement-app
```

#### Solution - Predict

```bash
curl "http://localhost/predict" \
  -XGET \
  -d "age=30&sex=1&bmi=23&bp=100&s1=157&s2=70&s3=40&s4=4&s5=3&s6=88"

docker rm -f enablement-app
```

### Task 4 - Monitor the model with DR MLOps

Use the MLOps monitoring agent to monitor the model inside a docker container. Use rabbitmq as spooler.

Keep this flow in mind: DR <---> Monitoring Agent <---> Spooler <---> Instrumented app

#### 4.1 Create and deploy a new Model Package in DataRobot.

https://docs.datarobot.com/en/docs/mlops/deployment/registry/reg-create.html#create-model-packages
Remember to pick the correct Prediction type based on what you see on `model.py`

##### Solution

https://app.datarobot.com/model-registry/custom-models | Model Registry | Model Packages | Add new package | New external model package

- Package name: ""
- Build Environment: "Python"
- Training data: "diabetes.csv"
- Target feature: "Y"
- Prediction type: Regression

https://app.datarobot.com/model-registry/custom-models | Model Registry | Model Packages | <Your previously created model package> | Deployments | Create new deployment

- Deployment name: "enablementFriday - Diabetes - external"
- Prediction Environment: "Other"

#### 4.2 Build a docker image containing the monitoring agent

Download and extract DataRobot's Monitoring Agent tar file. This is available through the DataRobot MLOps UI via User icon | Developer Tools | External Monitoring Agent.

Build a docker image containing the monitoring agent itself as well as the agent's default config.

See `datarobot_mlops_package-7.3.5/tools/agent_docker/README.md`

##### Solution

```bash
tar xfvz ../datarobot_mlops_package-7.3.5-1333.tar.gz -C .
cd datarobot_mlops_package-7.3.5/tools/agent_docker/

# Provide default conf and actual agent to docker image
cp -a ../../conf .
cp -a ../../lib .

# Build docker image
docker build \
  -t datarobot-mlops-agent:7.3.5 \
  -f Dockerfile .

cd -
```
#### 4.3 Create spooler (rabbitmq)

https://hub.docker.com/_/rabbitmq

##### Solution

Remember, that you can address docker instances internally by their name.

```bash
docker network create enablement

docker run \
  --rm \
  --name enablement-rabbitmq \
  --network enablement \
  -p 5672:5672 \
  -p 8080:15672 \
  rabbitmq:3-management \
  ;
```

http://localhost:8080/

- guest
- guest

#### 4.4 Adapt the agent's config to use rabbitmq

##### Solution

```bash
MLOPS_HOST='app.datarobot.com'
MLOPS_API_TOKEN='NjE3MTM4Mzc2ZjhjYjM5NDM2NjQ2OGMwOjVNWlNYeHJBbm9hQS85UUNsM1hCOUhCY3VMY1hvNDhscFR5dTJkZmUwblU9'

# copy and adapt the default config
cp datarobot_mlops_package-7.3.5/conf/mlops.agent.conf.yaml .
sed \
  -i '' \
  -e "s#<MLOPS_HOST>#${MLOPS_HOST}#" \
  -e "s#<MLOPS_API_TOKEN>#${MLOPS_API_TOKEN}#" \
  mlops.agent.conf.yaml

vi mlops.agent.conf.yaml
...
  - type: "RABBITMQ_SPOOL"
    details: {name: "rabbit", queueName: "mlops", queueUrl: "amqp://enablement-rabbitmq"}
```

#### 4.5 Run the agent within docker using your config

##### Hint

See `datarobot_mlops_package-7.3.5/tools/agent_docker/README.md`

##### Solution

```bash
# Instantiate container
docker run \
  --rm \
  --name datarobot-mlops-agent \
  --network enablement \
  -v ${PWD}/mlops.agent.conf.yaml:/opt/datarobot/mlops/agent/conf/mlops.agent.conf.yaml \
  datarobot-mlops-agent:7.3.5
```

#### 4.6 Instrument and monitor the app

Or not! Start with the already instrumented `app-instrumented.py` and make it work, so that you see your queries logged in DR.
Create a new container `enablement-app:instrumented` that comes with all requirements added by the instrumention satisfied.

https://docs.datarobot.com/en/docs/mlops/deployment/mlops-agent/index.html#mlops-agent

##### Solution

adapt `app.py` to contain/use valid deployment ad model ids as well as the correct queue URL.

```bash
vi app-instrumented/app.py
...
DEPLOYMENT_ID = '61924d543e5e9828d5c5e84d'
MODEL_ID = '61924d3510fc1c63d820b4c8'
QUEUE_URL = "amqp://enablement-rabbitmq"
```

Wrap it all into a container

```bash
cat << 'EOF_Dockerfile' > Dockerfile
FROM python:3.7

# Ensure that the python output is sent straight to terminal (e.g. your
# container log) without being first buffered and that you can see the output
# of your application (e.g. flask logs) in real time.
ENV PYTHONUNBUFFERED 1

# Prevent Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install MLOps agent
#
# Mount hist fs into containter at build time. Otherwise we would be forced to
# COPY the agent into the container and RUN its installation. As these steps
# will mapped to two distinct FS layers in docker we will blow up our images
RUN --mount=type=bind,target=/host,source=./,ro \
    ls -la /host && \
    pip install --find-links=/host/wheels --no-cache-dir /host/datarobot_mlops_package-7.3.5/lib/datarobot_mlops-7.3.5-py2.py3-none-any.whl

COPY app-instrumented/* .
COPY model/* ./model/

EXPOSE 9091
CMD [ "python", "/usr/src/app/app.py", "run" ]
EOF_Dockerfile

# Build container
docker build -t enablement-app:instrumented -f Dockerfile .
```

```bash
docker run \
  --rm \
  --network enablement \
  --name enablement-app \
  --publish 80:9091 \
  enablement-app:instrumented
```

```bash
curl "http://localhost/predict" \
  -XGET \
  -d "age=30&sex=1&bmi=23&bp=100&s1=157&s2=70&s3=40&s4=4&s5=3&s6=88"

docker rm -f enablement-app
```

