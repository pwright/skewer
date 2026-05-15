<!-- NOTE: This file is generated from skewer-extend.yaml.  Do not edit it directly. -->

# Skupper Network Observer Extension

#### Add observability and console access to a running Skupper demo

This extension adds the Skupper Network Observer to your running demo,
providing a web console for monitoring and managing your Skupper network.
The Network Observer offers real-time visibility into service connectivity,
traffic flows, and network topology across your multi-cluster deployment.

## Contents

* [Step 1: Check Skupper site status](#step-1-check-skupper-site-status)
* [Step 2: Install Skupper Network Observer and expose the console](#step-2-install-skupper-network-observer-and-expose-the-console)

## Step 1: Check Skupper site status

_**west:**_

~~~ shell
skupper site status
~~~

_**east:**_

~~~ shell
skupper site status
~~~

## Step 2: Install Skupper Network Observer and expose the console

_**west:**_

~~~ shell
helm install skupper-network-observer oci://quay.io/skupper/helm/network-observer --version 2.2.0
oc create route passthrough skupper-console --service=skupper-network-observer --port=https
kubectl get secret skupper-network-observer-auth -o jsonpath='{.data.htpasswd}' | base64 -d | sed 's/\(.*\):{PLAIN}\(.*\)/\1 \2\n/'
skupper link generate > ~/link.yaml
~~~
