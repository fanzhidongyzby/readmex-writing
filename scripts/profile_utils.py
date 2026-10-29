#!/usr/bin/env python3
"""Public defaults and optional ignored local validation preferences."""
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GENERIC = {
    'image_profile': 'generic', 'require_title': False, 'require_cover': False,
    'cover_size': None, 'max_heading_units': None, 'heading_numbering': 'optional',
    'require_subheadings': False, 'require_introduction': False,
    'require_svg_sources': False, 'require_references': False,
    'strict_asset_naming': False, 'private_reference_domains': [],
}
EVOMAP = dict(GENERIC, image_profile='evomap', require_title=True, require_cover=True,
              cover_size=[1200,511], max_heading_units=10, heading_numbering='required',
              require_subheadings=True, require_introduction=True, require_svg_sources=True,
              require_references=True, strict_asset_naming=True)


def load_settings(data=None, profile=None, use_local=True):
    data = data or {}
    local = {}
    path = SKILL_DIR/'.local/profile.json'
    if use_local and path.is_file():
        local = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(local, dict):
            raise ValueError('Local profile must be an object')
    selected = profile or data.get('image_profile') or local.get('illustration_profile', 'generic')
    if selected not in ('generic', 'evomap'):
        raise ValueError('Image profile must be generic or evomap')
    settings = dict(EVOMAP if selected == 'evomap' else GENERIC)
    explicit_profile = profile is not None or 'image_profile' in data
    for key in settings:
        if key in local and (not explicit_profile or key == 'private_reference_domains'):
            settings[key] = local[key]
        if key in data:
            settings[key] = data[key]
    settings['image_profile'] = selected
    if settings['heading_numbering'] not in ('optional','required'):
        raise ValueError('Unknown heading numbering policy')
    limit = settings['max_heading_units']
    if limit is not None and (type(limit) is not int or limit <= 0):
        raise ValueError('Heading limit must be a positive integer or null')
    return settings
