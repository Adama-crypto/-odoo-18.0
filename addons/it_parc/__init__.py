# -*- coding: utf-8 -*-

from . import models
from . import wizards
from . import controllers

def post_init_hook(env):
    """Post-installation hook to initialize default values"""
    # Create default alert parameters if not exists
    Alert = env['it.alerte']
    if not Alert.search_count([]):
        Alert.create({
            'name': 'Alerte Garantie',
            'type': 'garantie',
            'delai_jours': 30,
            'active': True,
        })
        Alert.create({
            'name': 'Alerte Contrat',
            'type': 'contrat',
            'delai_jours': 60,
            'active': True,
        })
