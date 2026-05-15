#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from plano import *
from plano.github import *
from skewer import *

_debug_param = CommandParameter("debug", help="Produce extra debug output on failure")

@command
def generate(*input_file, output=None):
    """
    Generate markdown documentation from a skewer or extension YAML file

    If input is a full skewer.yaml file, generates README.md.
    If input is an extension file, generates <input>.md.

    Usage:
      ./plano generate                     # Uses skewer.yaml
      ./plano generate skewer-extend.yaml  # Generates skewer-extend.md
    """
    # Handle input file parameter
    if input_file:
        input = input_file[0]
    else:
        input = "skewer.yaml"

    # Determine output filename
    if output is None:
        if input == "skewer.yaml":
            output = "README.md"
        else:
            output = input.replace(".yaml", ".md")

    # Detect file type and generate accordingly
    data = read_yaml(input)

    if "sites" in data:
        # Full skewer file
        generate_readme(input, output)
    else:
        # Extension file (only has 'steps')
        generate_extend_readme(input, output)

@command
def render(*input_file, quiet=False):
    """
    Render markdown documentation from YAML files

    If input is not provided or is skewer.yaml, generates README.md and README.html.
    If input is an extension file, generates only markdown (no HTML).

    Examples:
      ./plano render                      # skewer.yaml -> README.md + README.html
      ./plano render skewer-extend.yaml   # -> skewer-extend.md
      ./plano render skewer-getback.yaml  # -> skewer-getback.md
    """
    # Handle input file parameter
    if input_file:
        input = input_file[0]
    else:
        input = "skewer.yaml"

    # Generate markdown
    generate(input)

    # Only generate HTML for main README
    if input == "skewer.yaml":
        markdown = read("README.md")
        html = convert_github_markdown(markdown)
        write("README.html", html)

        if not quiet:
            print(f"file:{get_real_path('README.html')}")
    else:
        # For extension files, just show the markdown path
        output_file = input.replace(".yaml", ".md")
        if not quiet:
            print(f"file:{get_real_path(output_file)}")

@command
def clean():
    remove(find(".", "__pycache__"))
    remove("README.html")

@command(parameters=[_debug_param])
def run_(*kubeconfigs, debug=False):
    """
    Run the example steps

    If no kubeconfigs are provided, Skewer starts a local Minikube
    instance and runs the steps using it.
    """
    if not kubeconfigs:
        with Minikube("skewer.yaml") as mk:
            run_steps("skewer.yaml", kubeconfigs=mk.kubeconfigs, work_dir=mk.work_dir, debug=debug)
    else:
        run_steps("skewer.yaml", kubeconfigs=kubeconfigs, debug=debug)

@command(parameters=[_debug_param])
def demo(*kubeconfigs, debug=False):
    """
    Run the example steps and pause for a demo before cleaning up
    """
    with working_env(SKEWER_DEMO=1):
        run_(*kubeconfigs, debug=debug)

@command(parameters=[_debug_param])
def demo_extend(extend_file, debug=False):
    """
    Extend a running demo with additional steps

    The 'demo' command must be running and paused in another terminal.
    This command will attach to the running demo context and execute
    additional steps defined in the extend file.

    The extend file should be a YAML file with a 'steps' section,
    using the same format as skewer.yaml:

    steps:
      - title: My additional step
        commands:
          west:
            - run: kubectl get pods
          east:
            - run: skupper status

    Examples:
      ./plano demo_extend my-extra-steps.yaml
      ./plano demo_extend demo-scenario-2.yaml --debug
    """
    notice(f"Extending demo with steps from '{extend_file}'")

    # Load and validate demo context
    context = load_demo_context()
    validate_demo_context(context)

    notice(f"Attached to demo (PID {context['pid']}, work_dir={context['work_dir']})")

    # Create extended model
    model = create_extended_model(context, extend_file)

    # Run the extension steps
    try:
        for step in model.steps:
            run_step(model, step, context["work_dir"], check=True)

        notice("Extension steps completed successfully")
    except:
        if debug:
            print_debug_output(model)
        raise

@command(parameters=[_debug_param])
def test_(debug=False):
    """
    Test README generation and run the steps on Minikube

    If skewer-*.yaml files exist, their steps will be appended to
    skewer.yaml steps and run in sequence. This is useful for CI/CD
    where you want to run multiple test scenarios in one batch.
    """
    generate(output=make_temp_file())

    # Find and combine skewer-*.yaml extension files
    extension_files = sorted(list_dir(".", "skewer-*.yaml"))

    if not extension_files:
        # No extensions, just run normally
        run_(debug=debug)
        return

    notice(f"Found {len(extension_files)} extension file(s): {', '.join(extension_files)}")

    # Load base skewer.yaml
    base_data = read_yaml("skewer.yaml")
    base_steps = base_data.get("steps", [])

    # Collect steps from all extension files
    for ext_file in extension_files:
        notice(f"Loading steps from {ext_file}")
        ext_data = read_yaml(ext_file)
        ext_steps = ext_data.get("steps", [])
        if ext_steps:
            base_steps.extend(ext_steps)
            notice(f"  Added {len(ext_steps)} step(s)")

    # Create combined model with all steps
    base_data["steps"] = base_steps

    # Write to temporary file
    combined_file = make_temp_file()
    write_yaml(combined_file, base_data)

    notice(f"Running {len(base_steps)} total step(s)")

    # Run with combined file
    if True:  # No kubeconfigs
        with Minikube(combined_file) as mk:
            run_steps(combined_file, kubeconfigs=mk.kubeconfigs, work_dir=mk.work_dir, debug=debug)

    remove(combined_file)

@command
def update_skewer():
    """
    Update the embedded Skewer repo and GitHub workflow

    This results in local changes to review and commit.
    """
    update_external_from_github("external/skewer", "skupperproject", "skewer", "v2")
    copy("external/skewer/config/.github/workflows/main.yaml", ".github/workflows/main.yaml")
