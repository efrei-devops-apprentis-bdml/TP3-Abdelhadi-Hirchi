# DEVOPS - TP3

# Objectifs

Déployer sur azure container instance et mettre à disposition l’image sur Azure Container Registry en utilisant Github actions.

# Les repositories du TP

## GitHub repository

[GitHub - efrei-devops-apprentis-bdml/TP3-Abdelhadi-Hirchi](https://github.com/efrei-devops-apprentis-bdml/TP3-Abdelhadi-Hirchi)

# Création de l’Api

### L’api en Python

l’api est baser sur le wrapper, on récupère la latitude et longitude avec des request flask pour permettre de les ajouter dans l’url. On lance l’api sur le [localhost](http://localhost) port:8081 

```python
import requests
import json
from flask import Flask,  request, jsonify
import os
app = Flask(__name__)
api_key = os.environ['API_KEY']

with app.app_context():
    @app.route("/")
    def meteo():
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric" % (
            lat, lon, api_key)
        response = requests.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(data)
            }), 500

        return jsonify({
            'status': 'ok',
            'data': data
        })

if __name__ == "__main__":
    port=80
    app.run(host="0.0.0.0", port=port)
```

## Docker

pour faire marcher notre wrapper on a besoin d’un environnement Python, c’est pour ça on utilise docker pour créer cet environnement. 

 

### Le Dockerfile

```docker
FROM python:3.8-alpine
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

### Le fichier requirements.txt

C’est le ficher dans on trouve les librairie demander pour faire fonctionner notre code python 

```markdown
requests
datetime
flask
```

## Automatisation du push sur Azure

### Le workflow

GitHub actions permet d’automatiser le push de l’image sur dockerhub.

```yaml
# This workflow uses actions that are not certified by GitHub.
# They are provided by a third-party and are governed by
# separate terms of service, privacy policy, and support
# documentation.

name: Publish Docker image

on: push

jobs:
    build-and-deploy:
        runs-on: ubuntu-latest
        steps:
        # checkout the repo
        - name: 'Checkout GitHub Action'
          uses: actions/checkout@main
          
        - name: 'Login via Azure CLI'
          uses: azure/login@v1
          with:
            creds: ${{ secrets.AZURE_CREDENTIALS }}
        
        - name: 'Build and push image'
          uses: azure/docker-login@v1
          with:
            login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
            username: ${{ secrets.REGISTRY_USERNAME }}
            password: ${{ secrets.REGISTRY_PASSWORD }}
        - run: |
            docker build . -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/${{ secrets.IDENTIFIANT_EFREI }}:v1
            docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/${{ secrets.IDENTIFIANT_EFREI }}:v1
        - name: 'Deploy to Azure Container Instances'
          uses: 'azure/aci-deploy@v1'
          with:
            resource-group: ${{ secrets.RESOURCE_GROUP }}
            dns-name-label: devops-${{ secrets.IDENTIFIANT_EFREI }}
            image: ${{ secrets.REGISTRY_LOGIN_SERVER }}/${{ secrets.IDENTIFIANT_EFREI }}:v1
            registry-login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
            registry-username: ${{ secrets.REGISTRY_USERNAME }}
            registry-password: ${{ secrets.REGISTRY_PASSWORD }}
            secure-environment-variables: API_KEY=${{ secrets.API_KEY }}
            name: ${{ secrets.IDENTIFIANT_EFREI }}
            location: 'france central'
```

### Secrets

il faut configurer nos identifiants Azure, openweather et efrei sur Github secrets.

```yaml
 creds: ${{ secrets.AZURE_CREDENTIALS }}
 login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
 username: ${{ secrets.REGISTRY_USERNAME }}
 password: ${{ secrets.REGISTRY_PASSWORD }}
 secure-environment-variables: API_KEY=${{ secrets.API_KEY }}
 name: ${{ secrets.IDENTIFIANT_EFREI }}      
```

## Result

### Container instance:

![Untitled](DEVOPS%20-%20TP3%20b4d91a0afb7c4163932012a3815d4ec9/Untitled.png)

## Résultat d’appel API depuis un lien cloud

on utilise curl pour demander la température pour une latitude et longitude

```powershell
curl "http://devops-20200828.francecentral.azurecontainer.io/?lat=5.902785&lon=102.754175"
```

```powershell
abdel@LAPTOP-VKS08S91:~$ curl "http://devops-20200828.francecentral.azurecontainer.io/?lat=5.902785&lon=102.754175"
{"data":{"base":"stations","clouds":{"all":97},"cod":200,"coord":{"lat":5.9028,"lon":102.7542},"dt":1655467711,"id":1736405,"main":{"feels_like":29.65,"grnd_level":982,"humidity":73,"pressure":1009,"sea_level":1009,"temp":27.29,"temp_max":27.29,"temp_min":27.29},"name":"Jertih","rain":{"1h":0.12},"sys":{"country":"MY","sunrise":1655420157,"sunset":1655465023},"timezone":28800,"visibility":10000,"weather":[{"description":"light rain","icon":"10n","id":500,"main":"Rain"}],"wind":{"deg":121,"gust":4.69,"speed":4.29}},"status":"ok"}
```

## Bonus

### hadolint

```yaml
name: Docker Image CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:

  build:

    runs-on: ubuntu-latest

    steps:
      -
        name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      -
        name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      -
        name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      -
        name: hadolint
        uses: reviewdog/action-hadolint@v1
        with:
          reporter: github-pr-review
      -
        name: Build and push
        uses: docker/build-push-action@v3
        with:
          push: true
          tags: abdelhadihirchi/efrei-devops-tp2
```

### Sécurité

Toute les données sensibles sont hors image ou code .