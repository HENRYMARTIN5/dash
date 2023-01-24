"""
Dash: The Universal Package Manager

A powerful and lightweight package manager for any Linux distribution.
"""

from betterlib import logging, config
import requests, json, argparse

logger = logging.Logger("./dash.log", "dash")
conf = config.ConfigFile("./config.json")
conf.ensure("repos")

class PkgRepo():
	"""
	A package repository.
	"""
	def __init__(self, name, url):
		"""
		Create a new package repository.
		"""

		self.name = name
		self.url = url

	def __str__(self):
		"""
		Return a string representation of the package repository.
		Formatting: "Package Repo <name> @ <url>"
		"""

		return f"Package Repo {self.name} @ {self.url}"

	def exists(self, pkg):
		"""
		Checks if a given package exists in the repository.
		"""

		logger.debug(f"Checking if package {pkg} exists in repo {self.name}...")
		if requests.get(f"{self.url}/packages/{pkg}.json").status_code == 404:
			logger.debug(f"Package {pkg} not found in repo {self.name}.")
			return False
		return True

	def get(self, pkg):
		"""
		Gets a given package's metadata from the repository.
		"""

		if not self.exists(pkg):
			raise Exception(f"Package {pkg} does not exist!")
		logger.debug(f"Getting package {pkg} from repo {self.name}...")
		data = requests.get(f"{self.url}/packages/{pkg}.json").json()
		logger.debug(f"Got package {pkg} from repo {self.name}.")

		return data
	
	def search(self, term):
		"""
		Searches the repository for a given term.
		"""

		logger.debug(f"Searching repo {self.name} for term {term}...")
		data = requests.get(f"{self.url}/all.json").json()

		results = []
		for pkgName in data:
			if term in pkgName:
				results.append(pkgName)
		
		logger.debug(f"Found {len(results)} results for term {term} in repo {self.name}.")

		return results
	
	def list(self):
		"""
		Lists all packages in the repository.
		"""

		logger.debug(f"Listing all packages in repo {self.name}...")
		data = requests.get(f"{self.url}/all.json").json()
		logger.debug(f"Found {len(data)} packages in repo {self.name}.")

		return data


class RepoCollection():
	"""
	A collection of package repositories.
	"""
	
	def __init__(self):
		"""
		Create a new repository collection.
		"""

		self.repos = {}
	
	def __str__(self):
		"""
		Return a string representation of the repository collection.
		Formatting: "Repo Collection: <repo1>, <repo2>, <repo3>, ..."
		"""

		return f"Repo Collection: {', '.join([str(repo) for repo in self.repos])}"

	def add(self, repo):
		"""
		Add a package repository to the collection.
		"""

		self.repos[repo.name] = repo
	
	def exists(self, pkg):
		"""
		Checks if a given package exists in any of the repositories.
		"""

		repoNames = []
		for repo in self.repos.values():
			logger.info("Checking if package exists in repo " + repo.name + "...")
			if repo.exists(pkg):
				logger.info("Package " + pkg + " exists in repo " + repo.name + ".")
				repoNames.append(repo.name)
		
		if len(repoNames) == 0:
			logger.info("Package " + pkg + " does not exist in any repos.")
			return False
		
		return repoNames

	def get(self, pkg, repo):
		"""
		Gets a given package's metadata from a specific repository.
		"""

		if not repo in self.repos:
			raise Exception(f"Repo {repo} does not exist!")

		return self.repos[repo].get(pkg)
	
	def search(self, term):
		"""
		Searches all repositories for a given term.
		"""

		results = {}
		for repo in self.repos.values():
			logger.info("Searching repo " + repo.name + " for term " + term + "...")
			results[repo.name] = repo.search(term)
		
		return results
	
	def list(self):
		"""
		Lists all packages in all repositories.
		"""

		results = {}
		for repo in self.repos.values():
			logger.info("Fetching packages in repo " + repo.name + "...")
			results[repo.name] = repo.list()
		
		return results


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Dash: The Universal Package Manager')
	parser.add_argument('action', help='The action to perform (install, remove, update, search, list, or info)')
	parser.add_argument('query', help='The package or search term to perform the action on')
	parser.add_argument('--repo', help='The repository to perform the action on')
	args = parser.parse_args()

	logger.info("Reading config file...")
	repos = RepoCollection()
	for repo in conf.get("repos"):
		repos.add(PkgRepo(repo["name"], repo["url"]))
	
	logger.info("Loaded " + str(len(repos.repos)) + " repo(s).")

	if args.action == "install":
		res = repos.exists(args.query)
		if res == False:
			logger.critical("Package " + args.query + " does not exist!")
			exit(1)

		if len(res) > 1 and not args.repo:
			logger.critical("Package " + args.query + " exists in multiple repos! Please specify a repo with --repo. Available repos: " + ", ".join(res))
			exit(1)

		if args.repo:
			if repos.repos[args.repo].exists(args.query):
				# Package exists in specified repo
				# TODO: Install package
				pass
			else:
				logger.critical("Package " + args.query + " does not exist in repo " + args.repo + "!")
				exit(1)
		else:
			# Package exists in only one repo
			
			

			

