from app.views import Resource, Provider, Location

# Add resources
for resource in ["food", "clothing", "legal services", "transportation", "medical care", "education and enrollment", "religious services", "counseling", "housing"]:
	r = Resource(name=resource)
	r.save()
