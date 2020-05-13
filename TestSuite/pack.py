from pathlib import Path
from typing import List, Optional

from TestSuite.integration import Integration
from TestSuite.JSONBased import JSONBased
from TestSuite.script import Script
from TestSuite.secrets import Secrets


class Pack:
    """A class that mocks a pack inside to content repo

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Args:
        packs_dir: A Path to the root of Packs dir
        name: name of the pack to create

    Attributes:
        path (str): A path to the content pack.
        secrets (Secrets): Exception error code.
        integrations: A list contains any created integration
        scripts:  A list contains any created Script

    """

    def __init__(self, packs_dir: Path, name: str, repo):
        # Initiate lists:
        self.repo = repo
        self.integrations: List[Integration] = list()
        self.scripts: List[Script] = list()
        self.classifiers: List[JSONBased] = list()
        self.dashboards: List[JSONBased] = list()
        self.incident_types: List[JSONBased] = list()
        self.incident_field: List[JSONBased] = list()
        self.indicator_field: List[JSONBased] = list()
        self.layouts: List[JSONBased] = list()
        # Create base pack
        self._pack_path = packs_dir / name
        self._pack_path.mkdir()
        self.path = str(self._pack_path)
        # Create repo structure
        self._integrations_path = self._pack_path / 'Integrations'
        self._integrations_path.mkdir()
        self._scripts_path = self._pack_path / 'Scripts'
        self._scripts_path.mkdir()
        self._playbooks_path = self._pack_path / 'Playbooks'
        self._playbooks_path.mkdir()
        self._classifiers_path = self._pack_path / 'Classifiers'
        self._classifiers_path.mkdir()
        self._dashboards_path = self._pack_path / 'Dashboards'
        self._dashboards_path.mkdir()
        self._incidents_field_path = self._pack_path / 'IncidentFields'
        self._incidents_field_path.mkdir()
        self._incident_types_path = self._pack_path / 'IncidentTypes'
        self._incident_types_path.mkdir()
        self._indicator_fields = self._pack_path / 'IndicatorFields'
        self._indicator_fields.mkdir()
        self.secrets = Secrets(self._pack_path)
        self.secrets.write_secrets([])

    def create_integration(
            self,
            name: Optional[str] = None,
            yml: Optional[dict] = None,
            code: str = '',
            readme: str = '',
            description: str = '',
            changelog: str = '',
            image: bytes = b''):
        if name is None:
            name = f'integration_{len(self.integrations)}'
        if yml is None:
            yml = {}
        integration = Integration(self._integrations_path, name, self.repo)
        integration.build(
            code,
            yml,
            readme,
            description,
            changelog,
            image
        )
        self.integrations.append(integration)
        return integration

    def create_script(
            self,
            name: Optional[str] = None,
            yml: Optional[dict] = None,
            code: str = '',
            readme: str = '',
            description: str = '',
            changelog: str = '',
            image: bytes = b''):
        if name is None:
            name = f'script{len(self.integrations)}'
        if yml is None:
            yml = {}
        script = Script(self._scripts_path, name, self.repo)
        script.build(
            code,
            yml,
            readme,
            description,
            changelog,
            image
        )
        self.scripts.append(script)
        return script

    def create_json_based(
            self,
            name,
            prefix: str,
            content: dict = None,
    ):
        if content is None:
            content = {}
        obj = JSONBased(self._pack_path, name, prefix)
        obj.write_json(content)
        return obj

    def create_classifier(
            self,
            name,
            content: dict = None
    ):
        prefix = 'classifier'
        classifier = self.create_json_based(name, prefix, content)
        self.classifiers.append(classifier)
        return classifier

    def create_dashboard(
            self,
            name,
            content: dict = None
    ):
        prefix = 'dashboard'
        dashboard = self.create_json_based(name, prefix, content)
        self.dashboards.append(dashboard)
        return dashboard

    def create_incident_field(
            self,
            name,
            content: dict = None,
    ):
        prefix = 'incident-field'
        incident_field = self.create_json_based(name, prefix, content)
        self.incident_field.append(incident_field)
        return incident_field

    def create_incident_type(
            self,
            name,
            content: dict = None):
        prefix = 'incident-type'
        incident_type = self.create_json_based(name, prefix, content)
        self.incident_types.append(incident_type)
        return incident_type

    def create_indicator_field(
            self,
            name,
            content: dict = None
    ):
        prefix = 'incident-field'
        indicator_field = self.create_json_based(name, prefix, content)
        self.indicator_field.append(indicator_field)
