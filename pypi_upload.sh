rm -f -r kiacopy.egg-info/* dist/*
python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
