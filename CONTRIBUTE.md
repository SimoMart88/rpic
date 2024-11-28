# Environment configuration
- Install UV (https://docs.astral.sh/uv)
- Install Python `uv python install 3.9`
- Create a virtual environment `uv venv --python 3.9`
- Run `uv sync` on the root folder of the project
- Install pre-commit `pre-commit install`

## EnvRC configuration file (.envrc)
```.dotenv
dotenv
uv sync
source .venv/bin/activate
```

# Code commit
Commit you code using `cz commit`.
This will automatically:
- Standardize the commit message
- Bump the version
- Update the changelog

See Commitizen documentation for more details (https://commitizen-tools.github.io/commitizen/)
