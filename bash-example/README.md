<!-- NOTE: This file is generated from skewer.yaml.  Do not edit it directly. -->

# Skewer Hello World

#### A minimal HTTP application deployed and a configuration created



#### Contents

* [Overview](#overview)
* [Prerequisites](#prerequisites)
* [Step 1: Start the HTTP web server without an `index.html`` file](#step-1-start-the-http-web-server-without-an-indexhtml-file)
* [Step 2: Create an `index.html` file](#step-2-create-an-indexhtml-file)
* [Summary](#summary)
* [Next steps](#next-steps)
* [About this example](#about-this-example)

## Overview

In this example, we see how you create contexts (sites) and run commands.
In the Server context (site), we delete the index.html file and run a 
web server. In the Config context (site), we convert md to html and wait
until user has tested the result on the web server.

## Prerequisites

* npm  
  brew install node
  https://github.com/nvm-sh/nvm
* python
  pyyaml

## Step 1: Start the HTTP web server without an `index.html`` file

_**Server:**_

~~~ shell
rm -f index.html
npm_config_yes=true npx  http-server -s -p 4567 . &
~~~

## Step 2: Create an `index.html` file

_**Server:**_

~~~ shell
npm_config_yes=true npx  markdown-to-html-cli --source index.md
read -p 'Navigate to http://localhost:4567 and then press enter to exit.' input
kill $(ps aux | grep '[e]xec http-server' | awk '{print $2}')
~~~

## Summary

More summary

## Next steps

Check out Skewer at [Skewer][skewer], a library for
documenting and testing Skupper examples.

[skewer]: https://github.com/skupperproject/skewer

More steps

## About this example

This example was produced using [Skewer][skewer], a library for
documenting and testing Skupper examples.

[skewer]: https://github.com/skupperproject/skewer

Skewer provides utility functions for generating the README and
running the example steps.  Use the `./plano` command in the project
root to see what is available.

To quickly stand up the example using Minikube, try the `./plano demo`
command.
