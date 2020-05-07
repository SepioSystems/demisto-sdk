"""

"""
from pathlib import Path
from typing import List, Optional

from TestSuite.global_secrets import GlobalSecrets
from TestSuite.pack import Pack


class Repo:
    """A class that mocks a content repo

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Args:
        tmpdir: A Path to the root of the repo

    Attributes:
        path: A path to the content pack.
        secrets: Exception error code.
        packs: A list of created packs
    """

    def __init__(self, tmpdir: Path):
        self.packs: List[Pack] = list()
        self._tmpdir = tmpdir
        self._packs_path = tmpdir / 'Packs'
        self._packs_path.mkdir()
        self.path = str(self._tmpdir)
        self.secrets = GlobalSecrets(tmpdir)
        self.secrets.write_secrets()
        self.global_secrets_path = self.secrets.path

    def create_pack(self, name: Optional[str] = None):
        if name is None:
            name = f'pack_{len(self.packs)}'
        pack = Pack(self._packs_path, name, repo=self)
        self.packs.append(pack)
        return pack