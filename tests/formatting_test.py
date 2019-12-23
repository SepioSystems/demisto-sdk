import os
import pytest

from tests.tests_constants import SOURCE_FORMAT_INTEGRATION_COPY, DESTINATION_FORMAT_INTEGRATION_COPY, \
    SOURCE_FORMAT_SCRIPT_COPY, DESTINATION_FORMAT_SCRIPT_COPY, SOURCE_PLAYBOOK_SCRIPT_COPY, \
    DESTINATION_PLAYBOOK_SCRIPT_COPY

from demisto_sdk.yaml_tools.update_script import ScriptYMLFormat
from demisto_sdk.yaml_tools.update_playbook import PlaybookYMLFormat
from demisto_sdk.yaml_tools.update_integration import IntegrationYMLFormat

BASIC_YML_TEST_PACKS = [
    (SOURCE_FORMAT_INTEGRATION_COPY, DESTINATION_FORMAT_INTEGRATION_COPY, IntegrationYMLFormat, 'New Integration_copy'),
    (SOURCE_FORMAT_SCRIPT_COPY, DESTINATION_FORMAT_SCRIPT_COPY, ScriptYMLFormat, 'New_script_copy'),
    (SOURCE_PLAYBOOK_SCRIPT_COPY, DESTINATION_PLAYBOOK_SCRIPT_COPY, PlaybookYMLFormat, 'File Enrichment-GenericV2_copy')
]


@pytest.mark.parametrize('source_path, destination_path, formatter, yml_title', BASIC_YML_TEST_PACKS)
def test_basic_yml_updates(source_path, destination_path, formatter, yml_title):
    base_yml = formatter(source_path)
    base_yml.update_yml()
    assert yml_title not in str(base_yml.yml_data)
    assert -1 == base_yml.id_and_version_location['version']


@pytest.mark.parametrize('source_path, destination_path, formatter, yml_title', BASIC_YML_TEST_PACKS)
def test_save_output_file(source_path, destination_path, formatter, yml_title):
    base_yml = formatter(source_path, destination_path)
    base_yml.save_yml_to_destination_file()
    saved_file_path = os.path.join(os.path.dirname(source_path), os.path.basename(destination_path))
    assert os.path.isfile(saved_file_path)
    os.remove(saved_file_path)


INTEGRATION_PROXY_SSL_PACK = [
    (SOURCE_FORMAT_INTEGRATION_COPY, 'insecure', 'Trust any certificate (not secure)', 2),
    (SOURCE_FORMAT_INTEGRATION_COPY, 'proxy', 'Use system proxy settings', 1)
]


@pytest.mark.parametrize('source_path, argument_name, argument_description, appearances', INTEGRATION_PROXY_SSL_PACK)
def test_proxy_ssl_descriptions(source_path, argument_name, argument_description, appearances):
    base_yml = IntegrationYMLFormat(source_path)
    base_yml.update_proxy_insecure_param_to_default()

    argument_count = 0
    for argument in base_yml.yml_data['configuration']:
        if argument_name == argument['name']:
            assert argument_description == argument['display']
            argument_count += 1

    assert argument_count == appearances


INTEGRATION_BANG_COMMANDS_ARGUMENTS = [
    (SOURCE_FORMAT_INTEGRATION_COPY, 'url', [
        ('default', True),
        ('isArray', True),
        ('required', True)
    ]),
    (SOURCE_FORMAT_INTEGRATION_COPY, 'email', [
        ('default', True),
        ('isArray', True),
        ('required', True),
        ('description', '')
    ])
]


@pytest.mark.parametrize('source_path, bang_command, verifications', INTEGRATION_BANG_COMMANDS_ARGUMENTS)
def test_proxy_ssl_descriptions(source_path, bang_command, verifications):
    base_yml = IntegrationYMLFormat(source_path)
    base_yml.set_reputation_commands_basic_argument_to_default()

    for command in base_yml.yml_data['script']['commands']:
        if bang_command == command['name']:
            command_arguments = command['arguments'][0]
            for verification in verifications:
                assert command_arguments[verification[0]] == verification[1]
