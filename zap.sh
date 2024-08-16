sudo chmod 777 $(pwd)
echo $(id -u):$(id -g)
docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:latest zap-api-scan.py -t https://duaauth.devgauss.com/v3/api-docs -f openapi -r zap_report.html
  
  sudo mkdir -p owasp-zap-report
  sudo mv zap_report.html owasp-zap-report

exit_code=$?
echo "Exit code: $exit_code"

if [ ${exit_code} -ne 0 ]; then
  echo "OWASP ZAP Report has either Low/Medium/High Risk. Please check the HTML Report"
  exit 1;
else
  echo "ZAP record did not report any risk"
fi;