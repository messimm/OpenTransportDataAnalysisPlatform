import argparse
import json
import sys
from importlib import import_module
from pkgutil import iter_modules
from DataLoaders import *

def importFromFolderByName(folder, name):
	my_class = None
	for (_, module_name, _) in iter_modules([folder]):
			module = import_module(f"{folder}.{module_name}")
			if name in dir(module):
				my_class = getattr(module, name)
	return my_class

def loadModulesFromConfig(config, folder):
	modules = []
	for m in config: 
		m_class = m["Name"]
		m_params = m["Parameters"]
		m_class = importFromFolderByName(folder, m_class)
		modules.append(m_class(m_params))	
	return modules


def pipelineFromConfig(cfg_total):
	modules = []
	for module in ["DataLoaders", "DataCheckers", "DataAnalyzers", "DataVisualizers"]:
		modules.append(loadModulesFromConfig(cfg_total[module], module))
	loaders, checkers, analyzers, visualizers = modules
	assert len(loaders) == len(checkers)
	assert len(analyzers) == 1
	if len(loaders)==1:
		loaders	= loaders[0]
		checkers = checkers[0]	
	results = analyzers[0].analyze(loaders, checkers)
	for vis,r in zip(visualizers, results):
		vis.visualize(r)

def main():
	config_path = sys.argv[1]
	with open(config_path, "r") as f:
		config = f.read()
	cfg_total = json.loads(config)
	pipelineFromConfig(cfg_total)



if __name__ == '__main__':
	main()