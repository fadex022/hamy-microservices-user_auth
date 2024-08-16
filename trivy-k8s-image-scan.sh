echo $DOCKER_IMAGE

docker run -v /var/run/docker.sock:/var/run/docker.sock -v $HOME/Library/Caches:/root/.cache/ aquasec/trivy:0.52.2 image --exit-code 0 --severity LOW,MEDIUM,HIGH --light $DOCKER_IMAGE
docker run -v /var/run/docker.sock:/var/run/docker.sock -v $HOME/Library/Caches:/root/.cache/ aquasec/trivy:0.52.2 image --exit-code 1 --severity CRITICAL --light $DOCKER_IMAGE

  exit_code=$?
  echo "Exit Code: $exit_code"

  if [ "${exit_code}" = 1 ]; then
    echo "Image scanning failed. Vulnerabilities found"
    exit 1;
  else
    echo "Image scanning passed. No vulnerabilities found"
  fi;