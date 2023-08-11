.ONESHELL:

CONDAPATH = $$(conda info --base)


install:
	conda env create -f environment.yaml
	${CONDAPATH}/envs/ml-executor/bin/pip install -r requirements.txt

update:
	conda env update --prune -f environment.yaml
	${CONDAPATH}/envs/ml-executor/bin/pip install -U -r requirements.txt

clean:
	conda env remove --name ml-executor
