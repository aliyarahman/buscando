# -*- coding: utf-8 -*-
# Contains email body, subject, and from-email text to be sent when users create new provider accounts, or volunteer accounts
# STILL NEEDS TO BE CHANGED: - All the [link] references in the email bodies - the 'from' values in the dictionaries
# ------------------------------------------ ENGLISH LANGUAGE EMAIL BODIES --------------------------------------------

admin_email_address = "information@buscandomaryland.com"


english_provider_confirmation_body = '''Welcome to Buscando!

Thank you for becoming part of the Buscando network and playing an essential role in the lives of children seeking refuge. These children have often traveled hundreds of miles to escape inconceivable violence and hardship and face an uncertain future. They depend on organizations like yours and concerned individuals to help them meet basic needs and find a new home in the U.S.

Here are the details of your account:

Organization: {provider_name}
Username: {org_username}
Resources Needed: {resources_needed}
Resources Available: {resources_available}

To view or change your profile, log in at http://www.buscandomaryland.com/login/.

Again, thank you for being a positive force in the lives of children seeking refuge.
'''

english_provider_admin_body = '''Hello,

{org_username} has just registered to join Buscando. Please log into the administrator interface at http://www.buscandomaryland.com/admin/ to approve this user.
'''

english_volunteer_confirmation_body = '''Dear {firstname},

Welcome to Buscando!

Thank you for becoming part of the Buscando network and playing an essential role in the lives of children seeking refuge. These children have often traveled hundreds of miles to escape inconceivable violence and hardship and face an uncertain future. They depend on concerned individuals like you to help them meet basic needs and find a new home in the U.S.

Here are the details of your account:

Email Address: {vol_username}
Location: {vol_location}
Resources you can provide: {resources_available}


To get started:

{getting_started}


Again, thank you for being a positive force in the lives of children seeking refuge.
'''

english_volunteer_admin_body = '''Hello,

{vol_username} has just registered to join Buscando. Please log into the administrator interface at http://www.buscandomaryland.com/admin/ to approve this user.
'''
# ------------------------------------------ SPANISH LANGUAGE EMAIL BODIES --------------------------------------------

spanish_provider_confirmation_body = '''Bienvenido a Buscando!

Gracias por formar parte de Buscando y por jugar un papel esencial en las vidas de los niños que buscan refugio. Estos niños han viajado cientos de millas para escapar de dificultades y condiciones de violencia inconcebibles y ahora enfrentan un futuro incierto. Ellos dependen de individuos preocupados y de organizaciones como la suya, para cubrir sus necesidades básicas y conseguir un nuevo hogar en Estados Unidos.

Estos son los detalles de su cuenta:

Organización: {provider_name}
Usuario: {org_username}
Recursos que necesita: {resources_needed}
Recursos disponibles: {resources_available}

Para ver o modificar su perfil, ingrese aquí http://www.buscandomaryland.com/login/.

Una vez más, gracias por ser una fuerza positiva en la vida de los niños que buscan refugio.
'''

spanish_volunteer_confirmation_body = '''Estimado(a) {firstname},

Bienvenido a Buscando!

Gracias por formar parte de la red de Buscando y por jugar un papel esencial en la vida de los niños que buscan refugio. Estos niños han viajado cientos de millas para escapar de dificultades y condiciones de violencia inconcebibles y ahora enfrentan un futuro incierto. Ellos dependen de individuos preocupados como tú, para cubrir sus necesidades básicas y conseguir un nuevo hogar en Estados Unidos.

Estos son los detalles de su cuenta:

Usuario: {vol_username}
{vol_location}
Recursos disponibles: {resources_available}

{getting_started}


Una vez más, gracias por ser una fuerza positiva en la vida de los niños que buscan refugio.
'''

#Keeping all text for e-mails in here, even though it leads to slightly messy variable passing
english_here_are_some_orgs = "Here are some organizations near you that could use your help:\n\n"

spanish_here_are_some_orgs = "Estas son algunas de las organizaciones que podrían beneficiarse de su colaboración:\n\n"

english_find_some_orgs = "Find places where you can help:"

english_find_more_orgs = "Or find more places where you can help at"

spanish_find_some_orgs = "Aquí podrá encontrár unas organizaciones interesadas en recibir su ayuda:"

spanish_find_more_orgs = "Aquí podrá encontrár más organizaciones interesadas en recibir su ayuda"

english_miles_from_you = "miles from you"

spanish_miles_from_you = "Distancia en millas entre usted y esta organización"

english_resources_needed = "Resources Needed:"

spanish_resources_needed = "Recursos Necesitados:"


#dictionaries for translating resources

spanish_resource_dict = {"food":"comida",
							"clothing":"ropa",
							"language":"idioma",
							"transportation":"servicios de transporte",
							"legal services":"servicios legales",
							"medical care":"atención médica",
							"education/enrollment":"educación / inscripciones",
							"religious services":"servicios religiosos",
							"counseling":"orientación",
							"recreation":"entretenimiento"}
							
english_resource_dict = {"food":"food",
							"clothing":"clothing",
							"language":"language",
							"transportation":"transportation",
							"legal services":"legal services",
							"medical care":"medical care",
							"education/enrollment":"education/enrollment",
							"religious services":"religious services",
							"counseling":"counseling",
							"recreation":"recreation"}

english_version_emails = {
	'provider_signup': {
		'confirmation':{
			'from':admin_email_address,
			'subject':'Thank you for joining Buscando!',
			'body':english_provider_confirmation_body
		},
		'admin': {
			'from':admin_email_address,
			'subject':'New Organization: Approval Needed',
			'body':english_provider_admin_body
		}
	},
	'volunteer_signup': {
		'confirmation': {
			'from':admin_email_address,
			'subject':'Thank you for joining Buscando!',
			'body':english_volunteer_confirmation_body,
			'here_are_some_orgs':english_here_are_some_orgs,
			'find_some_orgs':english_find_some_orgs,
			'find_some_more_orgs':english_find_more_orgs,
			'resources_needed':english_resources_needed,
			'miles_from_you':english_miles_from_you
		},
		'admin':{
			'from':admin_email_address,
			'subject':'New Volunteer: Approval Needed',
			'body':english_volunteer_admin_body
		}
	},
	'resource_translation':english_resource_dict
}
spanish_version_emails = {
	'provider_signup': {
		'confirmation':{
			'from':admin_email_address,
			'subject':'Gracias por unirte a Buscando!',
			'body':spanish_provider_confirmation_body
		},
		'admin': {
			'from':admin_email_address,
			'subject':'New Organization: Approval Needed',
			'body':english_provider_admin_body
		}
	},
	'volunteer_signup': {
		'confirmation': {
			'from':admin_email_address,
			'subject':'Gracias por unirte a Buscando!',
			'body':spanish_volunteer_confirmation_body,
			'here_are_some_orgs':spanish_here_are_some_orgs,
			'find_some_orgs':spanish_find_some_orgs,
			'find_some_more_orgs':spanish_find_more_orgs,
			'resources_needed':spanish_resources_needed,
			'miles_from_you':spanish_miles_from_you
		},
		'admin':{
			'from':admin_email_address,
			'subject':'New Volunteer: Approval Needed',
			'body':english_volunteer_admin_body
		}
	},
	'resource_translation':spanish_resource_dict
}