import glob
import os
from pathlib import Path

import pytest
from demisto_sdk.commands.common import tools
from demisto_sdk.commands.common.constants import (INTEGRATIONS_DIR,
                                                   LAYOUTS_DIR,
                                                   PACKS_PLAYBOOK_YML_REGEX,
                                                   PACKS_TEST_PLAYBOOKS_REGEX,
                                                   PLAYBOOKS_DIR)
from demisto_sdk.commands.common.git_tools import git_path
from demisto_sdk.commands.common.tools import (LOG_COLORS,
                                               filter_packagify_changes,
                                               find_type, get_depth,
                                               get_dict_from_file,
                                               get_entity_id_by_entity_type,
                                               get_entity_name_by_entity_type,
                                               get_files_in_dir,
                                               get_last_release_version,
                                               get_matching_regex, get_ryaml,
                                               retrieve_file_ending,
                                               run_command_os,
                                               server_version_compare)
from demisto_sdk.tests.constants_test import (INDICATORFIELD_EXTRA_FIELDS,
                                              SOURCE_FORMAT_INTEGRATION_COPY,
                                              VALID_DASHBOARD_PATH,
                                              VALID_INCIDENT_FIELD_PATH,
                                              VALID_INCIDENT_TYPE_PATH,
                                              VALID_INTEGRATION_TEST_PATH,
                                              VALID_LAYOUT_PATH, VALID_MD,
                                              VALID_PLAYBOOK_ID_PATH,
                                              VALID_REPUTATION_FILE,
                                              VALID_SCRIPT_PATH,
                                              VALID_WIDGET_PATH)


class TestGenericFunctions:
    PATH_TO_HERE = f'{git_path()}/demisto_sdk/tests/test_files/'
    FILE_PATHS = [
        (os.path.join(PATH_TO_HERE, 'fake_integration.yml'), tools.get_yaml),
        (os.path.join(PATH_TO_HERE, 'fake_json.json'), tools.get_json)
    ]

    @pytest.mark.parametrize('file_path, func', FILE_PATHS)
    def test_get_file(self, file_path, func):
        assert func(file_path)

    @pytest.mark.parametrize('dir_path', ['demisto_sdk', f'{git_path()}/demisto_sdk/tests/test_files'])
    def test_get_yml_paths_in_dir(self, dir_path):
        yml_paths, first_yml_path = tools.get_yml_paths_in_dir(dir_path, error_msg='')
        yml_paths_test = glob.glob(os.path.join(dir_path, '*yml'))
        assert sorted(yml_paths) == sorted(yml_paths_test)
        if yml_paths_test:
            assert first_yml_path == yml_paths_test[0]
        else:
            assert not first_yml_path

    data_test_get_dict_from_file = [
        (VALID_REPUTATION_FILE, 'json'),
        (VALID_SCRIPT_PATH, 'yml'),
        ('test', None),
        (None, None)
    ]

    @pytest.mark.parametrize('path, _type', data_test_get_dict_from_file)
    def test_get_dict_from_file(self, path, _type):
        output = get_dict_from_file(str(path))[1]
        assert output == _type, f'get_dict_from_file({path}) returns: {output} instead {_type}'

    data_test_find_type = [
        (VALID_DASHBOARD_PATH, 'dashboard'),
        (VALID_INCIDENT_FIELD_PATH, 'incidentfield'),
        (VALID_INCIDENT_TYPE_PATH, 'incidenttype'),
        (INDICATORFIELD_EXTRA_FIELDS, 'indicatorfield'),
        (VALID_INTEGRATION_TEST_PATH, 'integration'),
        (VALID_LAYOUT_PATH, 'layout'),
        (VALID_PLAYBOOK_ID_PATH, 'playbook'),
        (VALID_REPUTATION_FILE, 'reputation'),
        (VALID_SCRIPT_PATH, 'script'),
        (VALID_WIDGET_PATH, 'widget'),
        ('', '')
    ]

    @pytest.mark.parametrize('path, _type', data_test_find_type)
    def test_find_type(self, path, _type):
        output = find_type(str(path))
        assert output == _type, f'find_type({path}) returns: {output} instead {_type}'

    test_path_md = [
        VALID_MD
    ]

    @pytest.mark.parametrize('path', test_path_md)
    def test_filter_packagify_changes(self, path):
        modified, added, removed = filter_packagify_changes(modified_files=[], added_files=[], removed_files=[path])
        assert modified == []
        assert added == set()
        assert removed == [VALID_MD]

    @pytest.mark.parametrize('data, output', [({'a': {'b': {'c': 3}}}, 3), ('a', 0), ([1, 2], 1)])
    def test_get_depth(self, data, output):
        assert get_depth(data) == output

    @pytest.mark.parametrize('path, output', [('demisto.json', 'json'), ('wow', '')])
    def test_retrieve_file_ending(self, path, output):
        assert retrieve_file_ending(path) == output


class TestGetRemoteFile:
    def test_get_remote_file_sanity(self):
        hello_world_yml = tools.get_remote_file('Packs/HelloWorld/Integrations/HelloWorld/HelloWorld.yml')
        assert hello_world_yml
        assert hello_world_yml['commonfields']['id'] == 'HelloWorld'

    def test_get_remote_file_origin(self):
        hello_world_yml = tools.get_remote_file('Packs/HelloWorld/Integrations/HelloWorld/HelloWorld.yml', 'master')
        assert hello_world_yml
        assert hello_world_yml['commonfields']['id'] == 'HelloWorld'

    def test_get_remote_file_tag(self):
        gmail_yml = tools.get_remote_file('Integrations/Gmail/Gmail.yml', '19.10.0')
        assert gmail_yml
        assert gmail_yml['commonfields']['id'] == 'Gmail'

    def test_get_remote_file_origin_tag(self):
        gmail_yml = tools.get_remote_file('Integrations/Gmail/Gmail.yml', 'origin/19.10.0')
        assert gmail_yml
        assert gmail_yml['commonfields']['id'] == 'Gmail'

    def test_get_remote_file_invalid(self):
        invalid_yml = tools.get_remote_file('Integrations/File/File.yml', '19.10.0')
        assert not invalid_yml

    def test_get_remote_file_invalid_branch(self):
        invalid_yml = tools.get_remote_file('Integrations/Gmail/Gmail.yml', 'NoSuchBranch')
        assert not invalid_yml

    def test_get_remote_file_invalid_origin_branch(self):
        invalid_yml = tools.get_remote_file('Integrations/Gmail/Gmail.yml', 'origin/NoSuchBranch')
        assert not invalid_yml

    def test_get_remote_md_file_origin(self):
        hello_world_readme = tools.get_remote_file('Packs/HelloWorld/README.md', 'master')
        assert hello_world_readme == {}

    def test_is_not_test_file(self):
        test_file = tools.is_test_file('Packs/HelloWorld/Integrations/HelloWorld/search_alerts.json')
        assert not test_file

    def test_is_test_file(self):
        test_file = tools.is_test_file('Packs/HelloWorld/Integrations/HelloWorld/test_data/search_alerts.json')
        assert test_file


class TestGetMatchingRegex:
    INPUTS = [
        ('Packs/XDR/Playbooks/XDR.yml', [PACKS_PLAYBOOK_YML_REGEX, PACKS_TEST_PLAYBOOKS_REGEX],
         PACKS_PLAYBOOK_YML_REGEX),
        ('Packs/XDR/NoMatch/XDR.yml', [PACKS_PLAYBOOK_YML_REGEX, PACKS_TEST_PLAYBOOKS_REGEX], False)
    ]

    @pytest.mark.parametrize("string_to_match, regexes, answer", INPUTS)
    def test_get_matching_regex(self, string_to_match, regexes, answer):
        assert get_matching_regex(string_to_match, regexes) == answer


class TestServerVersionCompare:
    V5 = "5.0.0"
    V0 = "0.0.0"
    EQUAL = 0
    LEFT_IS_LATER = 1
    RIGHT_IS_LATER = -1
    INPUTS = [
        (V0, V5, RIGHT_IS_LATER),
        (V5, V0, LEFT_IS_LATER),
        (V5, V5, EQUAL)
    ]

    @pytest.mark.parametrize("left, right, answer", INPUTS)
    def test_server_version_compare(self, left, right, answer):
        assert server_version_compare(left, right) == answer


def test_pascal_case():
    res = tools.pascal_case("PowerShell Remoting")
    assert res == "PowerShellRemoting"
    res = tools.pascal_case("good life")
    assert res == "GoodLife"
    res = tools.pascal_case("good_life-here v2")
    assert res == "GoodLifeHereV2"


class TestPrintColor:
    def test_print_color(self, mocker):
        mocker.patch('builtins.print')

        tools.print_color('test', LOG_COLORS.GREEN)

        print_args = print.call_args[0][0]
        assert print_args == u'{}{}{}'.format(LOG_COLORS.GREEN, 'test', LOG_COLORS.NATIVE)


class TestReleaseVersion:
    def test_get_last_release(self, mocker):
        mocker.patch('demisto_sdk.commands.common.tools.run_command', return_value='1.2.3\n4.5.6\n3.2.1\n20.0.0')

        tag = get_last_release_version()

        assert tag == '20.0.0'


class TestEntityAttributes:
    @pytest.mark.parametrize('data, entity', [({'commonfields': {'id': 1}}, INTEGRATIONS_DIR),
                                              ({'typeId': 1}, LAYOUTS_DIR), ({'id': 1}, PLAYBOOKS_DIR)])
    def test_get_entity_id_by_entity_type(self, data, entity):
        assert get_entity_id_by_entity_type(data, entity) == 1

    @pytest.mark.parametrize('data, entity', [({'typeId': 'wow'}, LAYOUTS_DIR), ({'name': 'wow'}, PLAYBOOKS_DIR)])
    def test_get_entity_name_by_entity_type(self, data, entity):
        assert get_entity_name_by_entity_type(data, entity) == 'wow'


class TestGetFilesInDir:
    def test_project_dir_is_file(self):
        project_dir = 'demisto_sdk/commands/download/downloader.py'
        assert get_files_in_dir(project_dir, ['py']) == [project_dir]

    def test_not_recursive(self):
        project_dir = 'demisto_sdk/commands/download'
        files = [f'{project_dir}/__init__.py', f'{project_dir}/downloader.py', f'{project_dir}/README.md']
        assert sorted(get_files_in_dir(project_dir, ['py', 'md'], False)) == sorted(files)

    def test_recursive(self):
        integrations_dir = 'demisto_sdk/commands/download/tests/tests_env/content/Packs/TestPack/Integrations'
        integration_instance_dir = f'{integrations_dir}/TestIntegration'
        files = [f'{integration_instance_dir}/TestIntegration.py',
                 f'{integration_instance_dir}/TestIntegration_testt.py']
        assert sorted(get_files_in_dir(integrations_dir, ['py'])) == sorted(files)


run_command_os_inputs = [
    ('ls', os.getcwd()),
    ('ls', Path(os.getcwd()))
]


@pytest.mark.parametrize('command, cwd', run_command_os_inputs)
def test_run_command_os(command, cwd):
    """Tests a simple command, to check if it works
    """
    stdout, stderr, return_code = run_command_os(
        command,
        cwd=cwd
    )
    assert 0 == return_code
    assert stdout
    assert not stderr


class TestGetFile:
    def test_get_ryaml(self):
        file_data = get_ryaml(SOURCE_FORMAT_INTEGRATION_COPY)
        assert file_data
        assert file_data.get('name') is not None
