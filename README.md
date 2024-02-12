docker build . --tag ingredients:latest
docker tag ingredients:latest rg.fr-par.scw.cloud/ingredients/ingredients:latest
docker push rg.fr-par.scw.cloud/ingredients/ingredients:latest