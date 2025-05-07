# Environment configuration
- Install UV (https://docs.astral.sh/uv)
- Install Python `uv python install 3.9`
- Create a virtual environment `uv venv --python 3.9`
- Run `uv sync --all-groups` on the root folder of the project
- Install pre-commit `pre-commit install`

## EnvRC configuration file (.envrc)
```.dotenv
dotenv
uv sync --all-groups
source .venv/bin/activate
```

## Functional test
In order to run functional tests with Selenium on your local environment, use '--selenium' option when running pytest
`pytest --selenium`

# Known Issues

## uWSGI installation
If uWSGI dependency installation fails for an LD problem, run the following command before the "uv sync":
```shell
uv tool install 'git+https://github.com/bluss/sysconfigpatcher'
sysconfigpatcher $HOME/.local/share/uv/python/<python installation reference>
```

See here for more details: https://github.com/astral-sh/uv/issues/8966#issuecomment-2466513707

# Code commit
Commit you code using `cz commit`.
This will automatically:
- Standardize the commit message
- Bump the version
- Update the changelog

See Commitizen documentation for more details (https://commitizen-tools.github.io/commitizen/)

# ClassDiagram
Install OS level dependency with the following command:
```shell
sudo apt install graphviz graphviz-dev
```

Make sure django_extensions library is properly included into the active application list:
```.dotenv
LOCAL_APPS='django_extensions'
```

Run the following command to generate the diagram and save into the docs folder:
```shell
./manage.py graph_models rpi_controller --rankdir "BT" -o docs/ClassDiagram.png
```
