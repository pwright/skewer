<!-- NOTE: This file is generated from skewer-getback.yaml.  Do not edit it directly. -->

# Get-Back Multi-Cluster Demonstration

#### Deploy an interactive load balancing visualization tool across Skupper sites

This extension deploys the Get-Back service to both west and east sites,
demonstrating Skupper's multi-cluster load balancing capabilities. Get-Back
is a dual-protocol counter service with HTTP/TCP endpoints and an interactive
web dashboard that visualizes request distribution across sites in real-time.

## Contents

* [Step 1: Deploy Get-Back service to west site](#step-1-deploy-get-back-service-to-west-site)
* [Step 2: Deploy Get-Back service to east site](#step-2-deploy-get-back-service-to-east-site)
* [Step 3: Wait for deployments to be ready](#step-3-wait-for-deployments-to-be-ready)
* [Step 4: Verify Skupper connectors and listeners](#step-4-verify-skupper-connectors-and-listeners)
* [Step 5: Access the Get-Back dashboard](#step-5-access-the-get-back-dashboard)

## Step 1: Deploy Get-Back service to west site

The Get-Back service is a demonstration tool for visualizing
load balancing across multiple sites. We deploy the full stack
to the west site, including the deployment, local service
(dashboard only), Skupper connectors, and Skupper listeners.

The local service exposes only the dashboard (port 9093) for
direct access. The backend HTTP/TCP services are exposed via
Skupper listeners, which aggregate traffic from all connected
sites (east and west), enabling multi-cluster load balancing.

_**west:**_

~~~ shell
kubectl apply -f west/deployment.yaml
kubectl apply -f west/service.yaml
kubectl apply -f west/connectors.yaml
kubectl apply -f west/listeners.yaml
~~~

_Sample output:_

~~~ console
$ kubectl apply -f west/deployment.yaml
deployment.apps/getback created

$ kubectl apply -f west/service.yaml
service/getback-dashboard created

$ kubectl apply -f west/connectors.yaml
connector.skupper.io/west-backend created
connector.skupper.io/west-backend-http created

$ kubectl apply -f west/listeners.yaml
multikeylistener.skupper.io/mkl-backend created
multikeylistener.skupper.io/mkl-backend-http created
~~~

## Step 2: Deploy Get-Back service to east site

In the east site, we deploy a minimal configuration: just the
deployment and Skupper connectors. The connectors expose the
local pods to the Skupper network using routing keys.

There is no local service or listeners in east - traffic is
aggregated through the west site's listeners.

_**east:**_

~~~ shell
kubectl apply -f east/deployment.yaml
kubectl apply -f east/connectors.yaml
~~~

_Sample output:_

~~~ console
$ kubectl apply -f east/deployment.yaml
deployment.apps/getback created

$ kubectl apply -f east/connectors.yaml
connector.skupper.io/east-backend created
connector.skupper.io/east-backend-http created
~~~

## Step 3: Wait for deployments to be ready

Wait for the Get-Back pods to be running and ready in both sites
before proceeding. This ensures the health probes are passing and
the services are ready to accept traffic.

_**west:**_

~~~ shell
~~~

_**east:**_

~~~ shell
~~~

Both deployments are now available. The pods are running and
the readiness probes on port 9091 are responding.

## Step 4: Verify Skupper connectors and listeners

Check that the Skupper connectors and listeners were created
successfully. The connectors expose local pods to the Skupper
network, while the listeners (in west) aggregate traffic from
multiple sites.

_**west:**_

~~~ shell
kubectl get connectors
kubectl get listeners
kubectl get pods -l app=getback
~~~

_**east:**_

~~~ shell
kubectl get connectors
kubectl get pods -l app=getback
~~~

You should see:
- **West**: 2 connectors, 2 listeners, 1 pod
- **East**: 2 connectors, 1 pod

The listeners in west provide aggregated endpoints that load
balance across both sites.

## Step 5: Access the Get-Back dashboard

Use port-forward to access the interactive Get-Back dashboard.
The dashboard provides a visual demonstration of load balancing,
showing real-time request distribution across pods and sites.

The dashboard service is exposed locally via the getback-dashboard
ClusterIP service on port 9093. The backend services (HTTP/TCP) are
accessed through Skupper listeners for cross-site load balancing.

_**west:**_

~~~ shell
kubectl port-forward service/getback-dashboard 9093:9093
~~~

You can now access the dashboard by navigating to
[http://localhost:9093](http://localhost:9093) in your browser.

**Service architecture**:
- Dashboard: accessed via local `getback-dashboard` service (port 9093)
- Backend HTTP/TCP: accessed via Skupper listeners for cross-site load balancing

**Aggregated endpoints** (from Skupper listeners):
- HTTP: `mkl-backend-http:9091`
- TCP: `mkl-backend:9092`

**Dashboard features**:
- Send concurrent HTTP/TCP requests
- View real-time request distribution across sites
- Monitor load balancing between east and west clusters

**Testing the setup**:
1. Open the dashboard at http://localhost:9093/
2. Set the HTTP backend to `mkl-backend-http:9091`
3. Click "Send HTTP Request" multiple times
4. Watch the distribution panel show traffic spreading across both sites

This architecture demonstrates the separation between local services
(dashboard access) and Skupper-managed services (backend endpoints),
preventing interference with Skupper's load balancing.
