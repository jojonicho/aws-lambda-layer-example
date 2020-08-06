# Deploy Lambda Layer To AWS

## requirements

- Docker to run and will create a folder named python
- aws-cli to deploy function, or
- serverless cli + serverless.yml file (recommended)

```sh
docker run --rm -v "$PWD":/var/task "lambci/lambda:build-python3.7" /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.7/site-packages/ --upgrade; exit"
```

Zip the file

```sh
zip -r layer.zip python
```

Deploy it to aws

```sh
aws lambda publish-layer-version --layer-name yourlayername --zip-file fileb://layer.zip --compatible-runtimes python3.7
```

viola!
