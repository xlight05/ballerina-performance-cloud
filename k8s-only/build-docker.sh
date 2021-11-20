cp -r ../tests .
docker build -t xlight05/k8s-only .
rm -rf tests/