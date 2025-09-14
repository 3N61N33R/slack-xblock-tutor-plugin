import os
from glob import glob

import click
import importlib_resources
from tutor import hooks

from .__about__ import __version__

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'SLACK_XBLOCK_TUTOR_PLUGIN_'.
        ("SLACK_XBLOCK_TUTOR_PLUGIN_VERSION", __version__),
        # Define the individual settings
        (
            "SLACK_XBLOCK_TUTOR_PLUGIN_DEFAULT_WORKSPACE_URL",
            "https://coding-campi.slack.com",
        ),
        ("SLACK_XBLOCK_TUTOR_PLUGIN_ENABLE_AUTO_CHANNELS", True),
        ("SLACK_XBLOCK_TUTOR_PLUGIN_TRACK_ANALYTICS", True),
        # Define the SLACK_XBLOCK_CONFIG dictionary directly with the variables
        # This will be rendered once when the env is saved.
        (
            "SLACK_XBLOCK_TUTOR_PLUGIN__CONFIG",
            {
                "DEFAULT_WORKSPACE_URL": "{{ SLACK_XBLOCK_TUTOR_PLUGIN_DEFAULT_WORKSPACE_URL }}",
                "ENABLE_AUTO_CHANNELS": "{{ SLACK_XBLOCK_TUTOR_PLUGIN_ENABLE_AUTO_CHANNELS }}",
                "TRACK_ANALYTICS": "{{ SLACK_XBLOCK_TUTOR_PLUGIN_TRACK_ANALYTICS }}",
            },
        ),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'SLACK_XBLOCK_TUTOR_PLUGIN_'.
        # For example:
        ### ("SLACK_XBLOCK_TUTOR_PLUGIN_SECRET_KEY", "{{ 24|random_string }}"),
    ]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        ### ("PLATFORM_NAME", "My platform"),
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutorslack_xblock_tutor_plugin/templates/slack-xblock-tutor-plugin/tasks/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutorslack_xblock_tutor_plugin/templates/slack-xblock-tutor-plugin/tasks/lms/init.sh
    # And then add the line:
    ### ("lms", ("slack-xblock-tutor-plugin", "tasks", "lms", "init.sh")),
]


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = str(
        importlib_resources.files("tutorslack_xblock_tutor_plugin")
        / os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


########################################
# DOCKER IMAGE MANAGEMENT
########################################


# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/slack-xblock-tutor-plugin/build/myimage,
        # and then write:
        ### (
        ###     "myimage",
        ###     ("plugins", "slack-xblock-tutor-plugin", "build", "myimage"),
        ###     "docker.io/myimage:{{ SLACK_XBLOCK_TUTOR_PLUGIN_VERSION }}",
        ###     (),
        ### ),
    ]
)


# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ SLACK_XBLOCK_TUTOR_PLUGIN_VERSION }}",
        ### ),
    ]
)


# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ SLACK_XBLOCK_TUTOR_PLUGIN_VERSION }}",
        ### ),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("tutorslack_xblock_tutor_plugin") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    [
        # Only add your 'templates' directory as a Jinja template root.
        str(importlib_resources.files("tutorslack_xblock_tutor_plugin") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        # This copies the entire 'build' directory from the root of your plugin
        # (tutor-contrib-slack-xblock-tutor-plugin/build)
        # to a specific location within the Tutor environment's build context:
        # ~/Library/Application Support/tutor-main/env/build/openedx/plugins/slack-xblock-tutor-plugin/build
        (
            str(
                importlib_resources.files(__name__).parent / "build"
            ),  # Source: Path to your plugin's 'build' dir
            "openedx/slack_xblock_assets",  # Destination: Relative to env/
        ),
        # Remove or adjust this line if you don't have an 'apps' directory at the root
        # of your plugin that needs to be copied into 'env/plugins'.
        # If you DO have it, make sure the destination is accurate relative to env/build.
        # For simplicity, you might temporarily remove this if it's not strictly needed for the XBlock.
        # ("slack-xblock-tutor-plugin/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutorslack_xblock_tutor_plugin/patches,
# apply a patch based on the file's name and contents.
for path in glob(
    str(importlib_resources.files("tutorslack_xblock_tutor_plugin") / "patches" / "*")
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################

# A job is a set of tasks, each of which run inside a certain container.
# Jobs are invoked using the `do` command, for example: `tutor local do importdemocourse`.
# A few jobs are built in to Tutor, such as `init` and `createuser`.
# You can also add your own custom jobs:


# To add a custom job, define a Click command that returns a list of tasks,
# where each task is a pair in the form ("<service>", "<shell_command>").
# For example:
### @click.command()
### @click.option("-n", "--name", default="plugin developer")
### def say_hi(name: str) -> list[tuple[str, str]]:
###     """
###     An example job that just prints 'hello' from within both LMS and CMS.
###     """
###     return [
###         ("lms", f"echo 'Hello from LMS, {name}!'"),
###         ("cms", f"echo 'Hello from CMS, {name}!'"),
###     ]


# Then, add the command function to CLI_DO_COMMANDS:
## hooks.Filters.CLI_DO_COMMANDS.add_item(say_hi)

# Now, you can run your job like this:
#   $ tutor local do say-hi --name="Team Blue"


#######################################
# CUSTOM CLI COMMANDS
#######################################

# Your plugin can also add custom commands directly to the Tutor CLI.
# These commands are run directly on the user's host computer
# (unlike jobs, which are run in containers).

# To define a command group for your plugin, you would define a Click
# group and then add it to CLI_COMMANDS:


### @click.group()
### def slack-xblock-tutor-plugin() -> None:
###     pass


### hooks.Filters.CLI_COMMANDS.add_item(slack-xblock-tutor-plugin)


# Then, you would add subcommands directly to the Click group, for example:


### @slack-xblock-tutor-plugin.command()
### def example_command() -> None:
###     """
###     This is helptext for an example command.
###     """
###     print("You've run an example command.")


# This would allow you to run:
#   $ tutor slack-xblock-tutor-plugin example-command

########################################
# XBLOCK CONFIGURATION
########################################

hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-dockerfile-post-python-requirements",
        """
# Install slack XBlock directly from GitHub.
RUN pip install git+https://github.com/3N61N33R/slack-xblock.git@main#egg=slack_xblock
""",
    )
)

# Install XBlock requirements
# hooks.Filters.ENV_PATCHES.add_item(
#     (
#         "openedx-dockerfile-post-python-requirements",
#         """
# # Copy the XBlock source code into the Docker image build context
# # The path below is relative to the Docker build context root.
# # It matches the destination path set by ENV_TEMPLATE_TARGETS above.
# COPY --chown=openedx:openedx slack_xblock_assets/openedx/xblock/slack_xblock /openedx/slack_xblock/

# # Install slack XBlock in editable mode from the copied path.
# RUN pip install -e /openedx/slack_xblock

# # Optional: Add the non-editable install from GitHub as a fallback/alternative for production.
# # RUN pip install git+https://github.com/3N61N33R/slack-xblock.git@main#egg=slack_xblock
# """,
#     )
# )

# hooks.Filters.ENV_PATCHES.add_item(
#     (
#         "openedx-dockerfile-post-python-requirements",
#         """# Install slack XBlock
# {% if SLACK_XBLOCK_TUTOR_PLUGIN_XBLOCK_SOURCE_PATH %}
# RUN pip install -e {{ SLACK_XBLOCK_TUTOR_PLUGIN_XBLOCK_SOURCE_PATH }}
# {% else %}
# RUN pip install slack_xblock==1.0.0
# {% endif %}
# """,
#     )
# )

# Add the XBlock to installed apps via patches
hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-lms-common-settings",
        """# Slack XBlock settings
INSTALLED_APPS.append('slack_xblock')

# Enable slack XBlock feature
FEATURES['ENABLE_SLACK_XBLOCK'] = True

# Slack XBlock configuration
SLACK_XBLOCK_TUTOR_PLUGIN__CONFIGG = {{ SLACK_XBLOCK_TUTOR_PLUGIN__CONFIG | tojson }}
""",
    )
)

hooks.Filters.ENV_PATCHES.add_item(
    (
        "openedx-cms-common-settings",
        """# Slack XBlock settings
INSTALLED_APPS.append('slack_xblock')

# Enable slack XBlock feature
FEATURES['ENABLE_SLACK_XBLOCK'] = True

# Slack XBlock configuration  
SLACK_XBLOCK_TUTOR_PLUGIN__CONFIG = {{ SLACK_XBLOCK_TUTOR_PLUGIN__CONFIG | tojson }}
""",
    )
)


# The mounted_directories hook is for AFTER the build, for live code changes.
# It's less crucial if you copy during build, but can be kept for consistency
# if you later add manual mounts for debugging.
@hooks.Filters.MOUNTED_DIRECTORIES.add()
def add_slack_xblock_mounted_directory(mounted_directories):
    # This mounts the XBlock source (which is already copied to env/build/openedx/openedx/xblock/slack_xblock)
    # into the running container.
    mounted_directories.append(("openedx", "openedx/xblock/slack_xblock"))
    return mounted_directories
