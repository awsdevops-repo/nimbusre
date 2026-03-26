Kubetool Agent prompts
* List all pods
* Show me the nodes in the cluster
* Get services in default namespace
* Describe the kubernetes service

Helm tool agent queries
* List Helm Releases
* Search for nginx chart
* get status of nginx release
* get values of nginx release
* Add the bitnami Helm repository
* Install nginx ingress controller from bitnami
* upgrade nginx release to latest from bitnami
* rollback nginx release to previous version

SRE tools agent prompts
-- test healing
* Scale up deployment of nginx by 1
* Scale down deployment of nginx by 1
* Check pod health
* Cordon node
-- Test cost analyzer
* list cost by namespace
* List unused PVCs
* check Node utilization
* check cluster cost estimate
* check node utilization
-- test logs
* get pod logs
* check health of pods in default namespaces
* list invalid pod operation
-- test Monitoring tool (eg Prometheus/Grafana)
* Available metrics
* CPU usage
* Memory usage
* List nginx pod restart count
* List alert status