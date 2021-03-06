from typing import Optional

import pytest
from demisto_sdk.commands.common.hook_validations.incident_type import \
    IncidentTypeValidator
from demisto_sdk.commands.common.hook_validations.structure import \
    StructureValidator
from mock import patch


def mock_structure(file_path=None, current_file=None, old_file=None):
    # type: (Optional[str], Optional[dict], Optional[dict]) -> StructureValidator
    with patch.object(StructureValidator, '__init__', lambda a, b: None):
        structure = StructureValidator(file_path)
        structure.is_valid = True
        structure.scheme_name = 'incident_type'
        structure.file_path = file_path
        structure.current_file = current_file
        structure.old_file = old_file
        return structure


data_is_valid_version = [
    (-1, True),
    (0, False),
    (1, False),
]


@pytest.mark.parametrize('version, is_valid', data_is_valid_version)
def test_is_valid_version(version, is_valid):
    structure = StructureValidator("")
    structure.current_file = {"version": version}
    validator = IncidentTypeValidator(structure)
    assert validator.is_valid_version() == is_valid, f'is_valid_version({version}) returns {not is_valid}.'


data_is_id_equal_name = [
    ('AWS EC2 Instance Misconfiguration', 'AWS EC2 Instance Misconfiguration', True),
    ('AWS EC2 Instance Misconfiguration', 'AWS EC2 Instance Wrong configuration', False)
]


@pytest.mark.parametrize('id_, name, is_valid', data_is_id_equal_name)
def test_is_id_equal_name(id_, name, is_valid):
    structure = StructureValidator("")
    structure.current_file = {"id": id_, "name": name}
    validator = IncidentTypeValidator(structure)
    assert validator.is_id_equals_name() == is_valid, f'is_id_equal_name returns {not is_valid}.'


data_is_including_int_fields = [
    ({"fromVersion": "5.0.0", "hours": 1, "days": 2, "weeks": 3, "hoursR": 1, "daysR": 2, "weeksR": 3}, True),
    ({"fromVersion": "5.0.0", "hours": 1, "days": 2, "weeks": "3", "hoursR": 1, "daysR": 2, "weeksR": 3}, False),
    ({"fromVersion": "5.0.0", "hours": 1, "days": 2, "weeks": 3, "hoursR": 1, "daysR": 2}, False),
]


@pytest.mark.parametrize('current_file, is_valid', data_is_including_int_fields)
def test_is_including_fields(current_file, is_valid):
    structure = mock_structure("", current_file)
    validator = IncidentTypeValidator(structure)
    assert validator.is_including_int_fields() == is_valid, f'is_including_int_fields returns {not is_valid}.'


IS_FROM_VERSION_CHANGED_NO_OLD = {}
IS_FROM_VERSION_CHANGED_OLD = {"fromVersion": "5.0.0"}
IS_FROM_VERSION_CHANGED_NEW = {"fromVersion": "5.0.0"}
IS_FROM_VERSION_CHANGED_NO_NEW = {}
IS_FROM_VERSION_CHANGED_NEW_HIGHER = {"fromVersion": "5.5.0"}
IS_CHANGED_FROM_VERSION_INPUTS = [
    (IS_FROM_VERSION_CHANGED_NO_OLD, IS_FROM_VERSION_CHANGED_NO_OLD, False),
    (IS_FROM_VERSION_CHANGED_NO_OLD, IS_FROM_VERSION_CHANGED_NEW, True),
    (IS_FROM_VERSION_CHANGED_OLD, IS_FROM_VERSION_CHANGED_NEW, False),
    (IS_FROM_VERSION_CHANGED_NO_OLD, IS_FROM_VERSION_CHANGED_NO_NEW, False),
    (IS_FROM_VERSION_CHANGED_OLD, IS_FROM_VERSION_CHANGED_NEW_HIGHER, True),
]


@pytest.mark.parametrize("current_from_version, old_from_version, answer", IS_CHANGED_FROM_VERSION_INPUTS)
def test_is_changed_from_version(current_from_version, old_from_version, answer):
    structure = StructureValidator("")
    structure.old_file = old_from_version
    structure.current_file = current_from_version
    validator = IncidentTypeValidator(structure)
    assert validator.is_changed_from_version() is answer
