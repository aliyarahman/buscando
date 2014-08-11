# -*- coding: utf-8 -*-

# Contains email body, subject, and from-email text to be sent when users create new provider accounts, or volunteer accounts
# STILL NEEDS TO BE CHANGED: - All the [link] references in the email bodies - the 'from' values in the dictionaries

# ------------------------------------------ ENGLISH LANGUAGE EMAIL BODIES --------------------------------------------

english_provider_confirmation_body = '''Welcome to Buscando!

Thank you for becoming part of the Buscando network and playing an essential role in the lives of children seeking refuge. These children have often traveled hundreds of miles to escape inconceivable violence and hardship and face an uncertain future. They depend on organizations like yours and concerned individuals to help them meet basic needs and find a new home in the U.S.

Here are the details of your account:

Username: {org_username}
Resources Needed: {resources_needed}
Resources Available: {resources_available}

To view or change your profile, log in at [link].

Again, thank you for being a positive force in the lives of children seeking refuge.
'''

english_provider_admin_body = '''Hello,

{org_username} has just registered to join Buscando. Please log into the administrator interface at [link] to approve this user.
'''

english_volunteer_confirmation_body = '''Dear {firstname},

Welcome to Buscando!

Thank you for becoming part of the Buscando network and playing an essential role in the lives of children seeking refuge. These children have often traveled hundreds of miles to escape inconceivable violence and hardship and face an uncertain future. They depend on concerned individuals like you to help them meet basic needs and find a new home in the U.S.

Here are the details of your account:

Username: {vol_username}
Resources Available: {resources_available}

To view or change your profile, log in at [link].

To get started:

Find places where you can help: [link]

Again, thank you for being a positive force in the lives of children seeking refuge.
'''

english_volunteer_admin_body = '''Hello,

{vol_username} has just registered to join Buscando. Please log into the administrator interface at [link] to approve this user.
'''

# ------------------------------------------ SPANISH LANGUAGE EMAIL BODIES --------------------------------------------

spanish_provider_confirmation_body = '''Bienvenido a Buscando!

Gracias por formar parte de Buscando y por jugar un papel esencial en las vidas de los niños que buscan refugio. Estos niños han viajado cientos de millas para escapar de dificultades y condiciones de violencia inconcebibles y ahora enfrentan un futuro incierto. Ellos dependen de individuos preocupados y de organizaciones como la suya, para cubrir sus necesidades básicas y conseguir un nuevo hogar en Estados Unidos.

Estos son los detalles de su cuenta:

Usuario: {org_username}
Recursos que necesita: {resources_needed}
Recursos disponibles: {resources_available}

Para ver o modificar su perfil, ingrese aquí [link].

Una vez más, gracias por ser una fuerza positiva en la vida de los niños que buscan refugio.
'''

spanish_provider_admin_body = '''Hola,

{org_username} se acaba de registrar para unirse a Buscando. Por favor, ingrese a la interfaz de administrador aquí [link] para aprobar a este nuevo usuario.
'''

spanish_volunteer_confirmation_body = '''Estimado(a) {firstname},

Bienvenido a Buscando!

Gracias por formar parte de la red de Buscando y por jugar un papel esencial en la vida de los niños que buscan refugio. Estos niños han viajado cientos de millas para escapar de dificultades y condiciones de violencia inconcebibles y ahora enfrentan un futuro incierto. Ellos dependen de individuos preocupados como tú, para cubrir sus necesidades básicas y conseguir un nuevo hogar en Estados Unidos.

Estos son los detalles de su cuenta:

Usuario: {vol_username}
Recursos disponibles: {resources_available}

Para ver o modificar su perfil, ingrese aquí [link].

Una vez más, gracias por ser una fuerza positiva en la vida de los niños que buscan refugio.

'''

spanish_volunteer_admin_body = '''Hola,

{vol_username} se acaba de registrar para unirse a Buscando. Por favor, ingrese a la interfaz de administrador aquí [link] para aprobar a este nuevo usuario.
'''

english_version_emails = {
    'provider_signup': {
        'confirmation':{
            'from':'test@buscando.io',
            'subject':'Thank you for joining Buscando!',
            'body':english_provider_confirmation_body
        },
        'admin': {
            'from':'test@buscando.io',
            'subject':'New Organization: Approval Needed',
            'body':english_provider_admin_body
        }
    },
    'volunteer_signup': {
        'confirmation': {
            'from':'test@buscando.io',
            'subject':'Thank you for joining Buscando!',
            'body':english_volunteer_confirmation_body
        },
        'admin':{
            'from':'test@buscando.io',
            'subject':'New Volunteer: Approval Needed',
            'body':english_volunteer_admin_body
        }
    }
}

spanish_version_emails = {
    'provider_signup': {
        'confirmation':{
            'from':'test@buscando.io',
            'subject':'Gracias por unirte a Buscando!',
            'body':spanish_provider_confirmation_body
        },
        'admin': {
            'from':'test@buscando.io',
            'subject':'Nueva Organización: requiere aprobación',
            'body':spanish_provider_admin_body
        }
    },
    'volunteer_signup': {
        'confirmation': {
            'from':'test@buscando.io',
            'subject':'Gracias por unirte a Buscando!',
            'body':spanish_volunteer_confirmation_body
        },
        'admin_notification':{
            'from':'test@buscando.io',
            'subject':'Nuevo Voluntario: requiere aprobación',
            'body':spanish_volunteer_admin_body
        }
    }
}