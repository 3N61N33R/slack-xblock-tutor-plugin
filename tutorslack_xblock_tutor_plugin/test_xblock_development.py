# ===== DEVELOPMENT TESTING SCRIPT =====
# File: test_xblock_development.py

import os
import subprocess
import sys


def test_workbench():
    """Test XBlock in workbench environment"""
    print("🚀 Testing XBlock in Workbench...")

    # Check if XBlock can be imported
    try:
        import slack_xblock  # Adjust this import based on your XBlock package name

        print("✅ XBlock import successful")
    except ImportError as e:
        print(f"❌ XBlock import failed: {e}")
        return False

    # Check workbench scenarios
    try:
        scenarios = slack_xblock.SlackXBlock.workbench_scenarios()
        print(f"✅ Found {len(scenarios)} workbench scenarios")
        for name, xml in scenarios:
            print(f"   - {name}")
    except Exception as e:
        print(f"❌ Workbench scenarios error: {e}")
        return False

    return True


def test_tutor_plugin():
    """Test Tutor plugin configuration"""
    print("🔧 Testing Tutor Plugin...")

    # Check if plugin is installed
    result = subprocess.run(
        ["tutor", "plugins", "list"], capture_output=True, text=True
    )

    if "slack" in result.stdout:
        print("✅ Slack plugin is installed")
    else:
        print("❌ Slack plugin not found in Tutor")
        return False

    # Check plugin status
    if "slack" in result.stdout and "enabled" in result.stdout:
        print("✅ Slack plugin is enabled")
    else:
        print("⚠️  Slack plugin not enabled - run: tutor plugins enable slack")

    return True


def setup_development_environment():
    """Set up complete development environment"""
    print("🛠️  Setting up development environment...")

    commands = [
        ["python", "-m", "venv", "xblock-dev"],
        ["pip", "install", "xblock-sdk"],
        ["pip", "install", "-e", "."],
    ]

    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            return False

    print("✅ Development environment ready!")
    return True


if __name__ == "__main__":
    print("🧪 XBlock Development Testing Suite\n")

    # Test workbench
    workbench_ok = test_workbench()

    # Test Tutor plugin (if available)
    try:
        tutor_ok = test_tutor_plugin()
    except FileNotFoundError:
        print("⚠️  Tutor not found - skipping plugin tests")
        tutor_ok = True

    if workbench_ok and tutor_ok:
        print("\n✅ All tests passed! Ready for development.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)
