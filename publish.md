# How To Publish This Package to PyPi

## Via GitHub Actions

- Bump the version in pyproject.toml as needed.
- Commit this change, e.g. `git commit -m "Release v99.99.99`
- Tag the commit, i.e. `git tag v99.99.99`
- Push the tag to GitHub, i.e. `git push origin v99.99.99`
- Wait for the GitHub action to run successfully.
- Go to the [Tags page](https://github.com/getditto/interface-gen/tags) and create a release.

## Manually from Command Line

Basic steps I follow are:

- Exit from regular virtualenv via `deactivate`
- Use a "publish" virtualenv that has the project dependencies plus `twine` and `build`, i.e.

```
deactivate  # if you're in the regular virtual env
python3 -m venv venv-publish
source venv-publish/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install twine build
```
- Build the package. Ensure you've bumped the version in `pyproject.toml` if needed,
  then:

```
python3 -m build
```

- Publish the package. Assuming you have a pypi.org (or test.pypi.org) account,
  and you've created an API key:

```
# Replace <version> with the version you're publishing:
python3 -m twine upload --repository testpypi dist/*<version>*
```

Note: If you're using test.pypi.org like the example above, you may run into
missing dependencies when trying to install your package from the test Pypi
instance. Adding the regular pypi.org url as an extra index option should fix
that:

```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ interface-gen==0.0.4

```
