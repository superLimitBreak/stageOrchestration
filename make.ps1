param ( [string]$target="run" )

# Set-ExecutionPolicy Unrestricted -Scope CurrentUser

$global:PYTHON_VERSION="3.7"
$global:ENV="_env_windows"
$global:DEPENDENCIES_PYTHON="docker/stageOrchestration.pip"
$global:PYTHON="$ENV/Scripts/python.exe"
$global:PIP="$ENV/Scripts/pip$PYTHON_VERSION.exe"


if ($target -eq "install" ) {
    #c:\python37\python.exe -m pip install --upgrade pip
    pip install virtualenv
    virtualenv --no-site-packages $ENV
    & $PYTHON -m pip install --upgrade pip
    & $PIP install --upgrade -r $DEPENDENCIES_PYTHON
}

if ($target -eq "run") {
    & $PYTHON server.py --config config.development.yaml
}
