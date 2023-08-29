# Contributing

Contributions are welcome. Please open an issue or a pull request.

## Development


Please read our [contributing guide](https://github.com/canonical/is-charms-contributing-guide) and
ensure that it is applied to your pull request. Beyond that, ensure that you generate source 
documentation as mentioned in the paragraph below.

### Generating src docs for every commit

Run the following command:

```bash
echo -e "tox -e src-docs\ngit add src-docs\n" >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Testing
We use `tox` to run tests. Use the following commands to run tests:

* `tox`: Runs all of the basic checks (`lint`, `unit`, `static`, and `coverage-report`).
* `tox -e fmt`: Runs formatting using `black` and `isort`.
* `tox -e lint`: Runs a range of static code analysis to check the code.
* `tox -e static`: Runs other checks such as `bandit` for security issues.
* `tox -e unit`: Runs the unit tests.
* `tox -e integration`: Runs the integration tests.
