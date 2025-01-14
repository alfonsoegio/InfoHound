import trio
import httpx
import requests
from holehe import core
from infohound.models import Emails

MODULE_ID = "findRegisteredSitesHoleheCustomTask"
MODULE_NAME = "holehe"
MODULE_DESCRIPTION = "Find registered services using Holehe tool" 
MODULE_TYPE = "Analysis"

def custom_task(domain_id):
	trio.run(findRegisteredSitesHolehe, domain_id)


async def findRegisteredSitesHolehe(domain_id):
	queryset = Emails.objects.filter(domain_id=domain_id)
	for entry in queryset.iterator():
		out = []
		email = entry.email

		modules = core.import_submodules("holehe.modules")
		websites = core.get_functions(modules)
		client = httpx.AsyncClient()

		for website in websites:
			await core.launch_module(website, email, client, out)
			print(out)
		await client.aclose()

		services = []
		for item in out:
			if item["exists"]:
				services.append(item["name"])

		entry.registered_services = services
		entry.save()