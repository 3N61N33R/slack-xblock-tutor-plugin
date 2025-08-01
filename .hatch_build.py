# https://hatch.pypa.io/latest/how-to/config/dynamic-metadata/

import os
import typing as t

from hatchling.metadata.plugin.interface import MetadataHookInterface

HERE = os.path.dirname(__file__)


class MetaDataHook(MetadataHookInterface):
    def update(self, metadata: dict[str, t.Any]) -> None:
        about = load_about()
        metadata["version"] = about["__version__"]


def load_about() -> dict[str, str]:
    about: dict[str, str] = {}
    with open(os.path.join(HERE, "tutorslack_xblock_tutor_plugin", "__about__.py"), "rt", encoding="utf-8") as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about
