# Skewer

[![main](https://github.com/skupperproject/skewer/actions/workflows/main.yaml/badge.svg)](https://github.com/skupperproject/skewer/actions/workflows/main.yaml)

A library for documenting and testing Skupper examples

A `skewer.yaml` file describes the steps and commands to achieve an
objective using Skupper.  Skewer takes the `skewer.yaml` file as input
and produces two outputs: a `README.md` file and a test routine.

#### Contents

- [Skewer](#skewer)
      - [Contents](#contents)
  - [An example example](#an-example-example)
  - [Setting up Skewer for your own example](#setting-up-skewer-for-your-own-example)
  - [Skewer YAML](#skewer-yaml)
  - [Standard steps](#standard-steps)
  - [Demo mode](#demo-mode)
  - [Extended testing with demo_extend and test](#extended-testing-with-demo_extend-and-test)
    - [Interactive development with demo_extend](#interactive-development-with-demo_extend)
    - [Batch testing for CI/CD with test](#batch-testing-for-cicd-with-test)
  - [Running against existing clusters](#running-against-existing-clusters)
  - [Troubleshooting](#troubleshooting)
    - [Subnet is already used](#subnet-is-already-used)
  - [Notes on speeding up Minikube](#notes-on-speeding-up-minikube)

## An example example

[Example `skewer.yaml` file](example/skewer.yaml)

[Example `README.md` output](example/README.md)

## Setting up Skewer for your own example

**Note:** This is how you set things up from scratch.  You can also
use the [Skupper example template][template] as a starting point.

[template]: https://github.com/skupperproject/skupper-example-template

Change directory to the root of your example project:

    cd <project-dir>/

Add the Skewer code as a subdirectory:

    mkdir -p external
    curl -sfL https://github.com/skupperproject/skewer/archive/v2.tar.gz | tar -C external -xz
    mv external/skewer-2 external/skewer

Symlink the Skewer and Plano libraries into your `python` directory:

    mkdir -p python
    ln -s ../external/skewer/python/skewer python/skewer
    ln -s ../external/skewer/python/plano python/plano

Copy the `plano` command into the root of your project:

    cp external/skewer/plano plano

Copy the standard config files:

    cp external/skewer/config/.plano.py .plano.py
    cp external/skewer/config/.gitignore .gitignore

Copy the standard workflow file:

    mkdir -p .github/workflows
    cp external/skewer/config/.github/workflows/main.yaml .github/workflows/main.yaml

Use your editor to create a `skewer.yaml` file in the root of your
project:

    emacs skewer.yaml

To use the `./plano` command, you must have the Python `pyyaml`
package installed.  Use `pip` (or `pip3` on some systems) to install
it:

    pip install pyyaml

Run the `./plano` command to see the available commands:

~~~ console
$ ./plano
usage: plano [-h] [-f FILE] [-m MODULE] {command} ...

Run commands defined as Python functions

options:
  -h, --help            Show this help message and exit
  -f FILE, --file FILE  Load commands from FILE (default '.plano.py')
  -m MODULE, --module MODULE
                        Load commands from MODULE

commands:
  {command}
    generate            Generate README.md from the data in skewer.yaml
    render              Render README.html from README.md
    clean               Clean up the source tree
    run                 Run the example steps
    demo                Run the example steps and pause for a demo before cleaning up
    demo_extend         Extend a running demo with additional steps from a YAML file
    test                Test README generation and run the steps on Minikube
    update-skewer       Update the embedded Skewer repo and GitHub workflow
~~~

## Skewer YAML

The top level of the `skewer.yaml` file:

~~~ yaml
title:              # Your example's title (required)
subtitle:           # Your chosen subtitle (optional)
workflow:           # The filename of your GitHub workflow (optional, default 'main.yaml')
overview:           # Text introducing your example (optional)
prerequisites:      # Text describing prerequisites (optional, has default text)
sites:              # A map of named sites (see below)
steps:              # A list of steps (see below)
summary:            # Text to summarize what the user did (optional)
next_steps:         # Text linking to more examples (optional, has default text)
~~~

For fields with default text such as `prerequisites` and `next_steps`,
you can include the default text inside your custom text by using the
`@default@` placeholder:

~~~ yaml
next_steps:
    @default@

    This Way to the Egress.
~~~

To disable the GitHub workflow and CI badge, set `workflow` to `null`.

A **site**:

~~~ yaml
<site-name>:
  title:            # The site title (optional)
  platform:         # "kubernetes" or "podman" (required)
  namespace:        # The Kubernetes namespace (required for Kubernetes sites)
  env:              # A map of named environment variables
~~~

Kubernetes sites must have a `KUBECONFIG` environment variable with a
path to a kubeconfig file.  A tilde (~) in the kubeconfig file path is
replaced with a temporary working directory during testing.

Podman sites must have a `SKUPPER_PLATFORM` variable with the value
`podman`.

Example sites:

~~~ yaml
sites:
  east:
    title: East
    platform: kubernetes
    namespace: east
    env:
      KUBECONFIG: ~/.kube/config-east
  west:
    title: West
    platform: podman
    env:
      SKUPPER_PLATFORM: podman
~~~

A **step**:

~~~ yaml
- title:            # The step title (required)
  preamble:         # Text before the commands (optional)
  commands:         # Named groups of commands.  See below.
  postamble:        # Text after the commands (optional)
~~~

An example step:

~~~ yaml
steps:
  - title: Expose the frontend service
    preamble: |
      We have established connectivity between the two namespaces and
      made the backend in `east` available to the frontend in `west`.
      Before we can test the application, we need external access to
      the frontend.

      Use `kubectl expose` with `--type LoadBalancer` to open network
      access to the frontend service.  Use `kubectl get services` to
      check for the service and its external IP address.
    commands:
      east: <list-of-commands>
      west: <list-of-commands>
~~~

The step commands are separated into named groups corresponding to the
sites.  Each named group contains a list of command entries.  Each
command entry has a `run` field containing a shell command and other
fields for awaiting completion or providing sample output.

You can also use a named step from the library of [standard
steps](#standard-steps):

~~~ yaml
- standard: kubernetes/access_your_kubernetes_clusters
~~~

A **command**:

~~~ yaml
- run:              # A shell command (required)
  apply:            # Use this command only for "readme" or "test" (default is both)
  output:           # Sample output to include in the README (optional)
  expect_failure:   # If true, check that the command fails and keep going (default false)
~~~

Only the `run` and `output` fields are used in the README content.
The `output` field is used as sample output only, not for any kind of
testing.

The `apply` field is useful when you want the readme instructions to
be different from the test procedure, or you simply want to omit
something.

There are also some special "await" commands that you can use to pause
for a condition you require before going to the next step.  They are
used only for testing and do not impact the README.

~~~ yaml
- await_resource:     # A resource for which to await readiness (optional)
                      # Example: await_resource: deployment/frontend
- await_ingress:      # A service for which to await an external hostname or IP (optional)
                      # Example: await_ingress: service/frontend
- await_http_ok:      # A service and URL template for which to await an HTTP OK response (optional)
                      # Example: await_http_ok: [service/frontend, "http://{}:8080/api/hello"]
~~~

Example commands:

~~~ yaml
commands:
  east:
    - run: skupper expose deployment/backend --port 8080
      output: |
        deployment backend exposed as backend
  west:
    - await_resource: service/backend
    - run: kubectl get service/backend
      output: |
        NAME          TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)         AGE
        backend       ClusterIP      10.102.112.121   <none>           8080/TCP        30s
~~~

## Standard steps

Skewer includes a library of standard steps with descriptive text and
commands that we use a lot for our examples.

The standard steps are defined in
[python/skewer/standardsteps.yaml](python/skewer/standardsteps.yaml).
They fall in three groups.

Steps for setting up platforms:

~~~
platform/access_your_kubernetes_clusters
platform/access_your_kubernetes_cluster
platform/create_your_kubernetes_namespaces
platform/create_your_kubernetes_namespace
platform/set_up_your_podman_environments
platform/set_up_your_podman_environment
platform/install_skupper_on_your_kubernetes_clusters
platform/install_skupper_on_your_kubernetes_cluster
platform/install_skupper_in_your_podman_environments
platform/install_skupper_in_your_podman_environment
~~~

Steps for primary Skupper operations:

~~~
skupper/create_your_sites/kubernetes_cli
skupper/create_your_sites/podman_cli
skupper/link_your_sites/kubernetes_cli
skupper/link_your_sites/podman_cli
skupper/cleaning_up/kubernetes_cli
skupper/cleaning_up/podman_cli
~~~

<!-- skupper/create_your_sites/kubernetes_yaml -->
<!-- skupper/create_your_sites/podman_yaml -->
<!-- skupper/link_your_sites/kubernetes_yaml -->
<!-- skupper/link_your_sites/podman_yaml -->
<!-- skupper/cleaning_up/kubernetes_yaml -->
<!-- skupper/cleaning_up/podman_yaml -->

Steps specific to the Hello World application:

~~~
hello_world/deploy_the_frontend_and_backend/kubernetes_cli
hello_world/expose_the_backend_service/kubernetes_cli
hello_world/access_the_frontend_service/kubernetes_cli
hello_world/cleaning_up/kubernetes_cli
~~~

<!-- hello_world/deploy_the_frontend_and_backend/kubernetes_yaml -->
<!-- hello_world/expose_the_backend_service/kubernetes_yaml -->
<!-- hello_world/access_the_frontend_service/kubernetes_yaml -->
<!-- hello_world/cleaning_up/kubernetes_yaml -->

Some of the steps have a suffix indicating their target platform and
interface: `kubernetes_cli`, `kubernetes_yaml`, `podman_cli`, and
`podman_yaml`.

**Note:** The `link_your_sites` and `cleaning_up` steps are less
generic than some of the other steps.  For example, `cleaning_up`
doesn't delete any application workoads.  Check that the text and
commands these steps produce are doing what you need for your example.
If not, you need to provide a custom step.

You can create custom steps based on the standard steps by overriding
the `title`, `preamble`, `commands`, or `postamble` fields.

~~~ yaml
- standard: skupper/cleaning_up/kubernetes_cli
  commands:
    east:
     - run: skupper delete
     - run: kubectl delete deployment/database
    west:
     - run: skupper delete
~~~

For string fields such as `preamble` and `postamble`, you can include
the standard text inside your custom text by using the `@default@`
placeholder:

~~~ yaml
- standard: skupper/cleaning_up/kubernetes_cli
  preamble: |
    @default@

    Note: You may also want to flirp your krupke.
~~~

A typical mix of standard and custom steps for a Kubernetes-based
example might look like this:

~~~ yaml
steps:
  - standard: platform/access_your_kubernetes_clusters
  - standard: platform/create_your_kubernetes_namespaces
  - <your-custom-deploy-step>
  - standard: platform/install_skupper_on_your_kubernetes_clusters
  - standard: platform/install_the_skupper_command_line_tool
  - standard: skupper/create_your_sites/kubernetes_cli
  - standard: skupper/link_your_sites/kubernetes_cli
  - <your-custom-expose-step>
  - <your-custom-access-step>
  - standard: skupper/cleaning_up/kubernetes_cli
~~~

## Demo mode

Skewer has a mode where it executes all the steps, but before cleaning
up and exiting, it pauses so you can inspect things.

It is enabled by setting the environment variable `SKEWER_DEMO` to any
value when you call `./plano run` or one of its variants.  You can
also use `./plano demo`, which sets the variable for you.

## Extended testing with demo_extend and test

Skewer provides two complementary approaches for extending your tests beyond the base `skewer.yaml` file:

### Interactive development with demo_extend

The `demo_extend` command allows you to attach to a running demo and execute additional test scenarios while keeping the clusters and services active. This is useful for iterative testing and exploration.

**Usage:**

In one terminal, start the demo:

```console
$ ./plano demo
```

The demo will execute all setup steps and then pause, displaying connection information.

In a separate terminal, run additional test scenarios:

```console
$ ./plano demo_extend skewer-extend.yaml
$ ./plano demo_extend skewer-load-test.yaml
$ ./plano demo_extend skewer-chaos.yaml
```

Each `demo_extend` invocation:
- Attaches to the running demo's environment (same kubeconfigs, namespaces, clusters)
- Executes the steps defined in the extension YAML file
- Exits while leaving the demo running for further testing

The extension YAML files follow the same format as `skewer.yaml` but only require a `steps` section (sites are inherited from the running demo):

```yaml
# skewer-extend.yaml
steps:
  - title: Check pod status
    commands:
      west:
        - run: kubectl get pods
      east:
        - run: kubectl get pods

  - title: Verify Skupper connectivity
    commands:
      west:
        - run: skupper site status
      east:
        - run: skupper link status
```

When finished, return to the first terminal and type `yes` to clean up and exit.

### Batch testing for CI/CD with test

The `test` command automatically discovers and runs all test scenarios in a single batch execution, making it ideal for CI/CD pipelines.

**Usage:**

```console
$ ./plano test
```

This command:
1. Generates the README (as before)
2. Discovers all `skewer-*.yaml` files in the current directory
3. Concatenates their steps to the base `skewer.yaml` steps
4. Runs all steps in sequence on Minikube
5. Cleans up automatically when complete

If no `skewer-*.yaml` files exist, `test` runs only the base `skewer.yaml` (backward compatible).

**Example project structure:**

```
skewer.yaml              # Base: setup clusters, deploy app, basic smoke test
skewer-extend.yaml       # Additional verification steps
skewer-load-test.yaml    # Load testing scenario
skewer-failure.yaml      # Chaos/failure testing
```

**GitHub Actions example:**

```yaml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install pyyaml
      - name: Run all tests
        run: ./plano test
```

The `test` command runs `skewer.yaml` + `skewer-extend.yaml` + `skewer-load-test.yaml` + `skewer-failure.yaml` automatically, in alphabetical order.

**When to use each approach:**

- Use `demo` + `demo_extend` for interactive development and debugging
- Use `test` for automated CI/CD pipelines and comprehensive test runs

Both approaches work with custom kubeconfigs as described in the next section.

## Running against existing clusters

By default, `./plano run` and `./plano demo` start a local Minikube instance automatically and use it for all Kubernetes sites. If you want to run against your own clusters instead, pass kubeconfig file paths as positional arguments.

Kubeconfigs are assigned to Kubernetes sites **in the order the sites are defined** in `skewer.yaml`. For example, given this site definition:

```
sites:    west:      platform: kubernetes      namespace: west      env:        KUBECONFIG: ~/.kube/config-west    east:      platform: kubernetes      namespace: east      env:        KUBECONFIG: ~/.kube/config-east
```

`west` is the first Kubernetes site and `east` is the second. To run with a remote OpenShift cluster for `west` and a local Minikube instance for `east`, first start Minikube and export its kubeconfig:

```
minikube start -p east  minikube -p east kubeconfig > ~/.kube/config-east-minikube
```

Then pass the kubeconfigs in site order (west first, east second):

```
./plano demo ~/.kube/config-west-openshift ~/.kube/config-east-minikube
```

Or equivalently for `run`:

```
./plano run ~/.kube/config-west-openshift ~/.kube/config-east-minikube
```

The provided kubeconfigs override the paths in `skewer.yaml` at runtime — the `skewer.yaml` file itself is not modified. Each kubeconfig must already be authenticated and have the correct namespace context set before running.



## Troubleshooting

### Subnet is already used

Error:

~~~ console
plano: notice: Starting Minikube
plano: notice: Running command 'minikube start -p skewer --auto-update-drivers false'
* Creating podman container (CPUs=2, Memory=16000MB) ...- E0229 05:44:29.821273   12224 network_create.go:113] error while trying to create podman network skewer 192.168.49.0/24: create podman network skewer 192.168.49.0/24 with gateway 192.168.49.1 and MTU of 0: sudo -n podman network create --driver=bridge --subnet=192.168.49.0/24 --gateway=192.168.49.1 --label=created_by.minikube.sigs.k8s.io=true --label=name.minikube.sigs.k8s.io=skewer skewer: exit status 125

Error: subnet 192.168.49.0/24 is already used on the host or by another config
~~~

Remove the existing Podman network.  Note that it might belong to
another user on the host.

~~~ shell
sudo podman network rm minikube
~~~

## Notes on speeding up Minikube

~~~ console
minikube config set cpus 4
minikube config set memory 8192
~~~
