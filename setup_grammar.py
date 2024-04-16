import datetime
import pathlib
import subprocess
from enum import Enum

import requests


class Antlr4Target(Enum):
    js = 'JavaScript'
    python = 'Python3'


build_options = {
    'antlr4_compiled_target_output': {
        Antlr4Target.js: 'cratedb_sqlparse_js',
        Antlr4Target.python: 'cratedb_sqlparse_py'
    },

    'antlr4_compiled_target_subdir': 'parser/generated_parser',

    # List of '.g4' files that will be built
    'files': [
        {
            'url': 'https://github.com/crate/crate/raw/{version}/libs/sql-parser/src/main/antlr/io/crate/sql/parser/antlr/SqlBaseLexer.g4',
            'filename': 'SqlBaseLexer.g4'
        },
        {
            'url': 'https://github.com/crate/crate/raw/{version}/libs/sql-parser/src/main/antlr/io/crate/sql/parser/antlr/SqlBaseParser.g4',
            'filename': 'SqlBaseParser.g4'
        }
    ]
}

PARSER_COMPILE_PATH = pathlib.Path(__file__).parent


def download_cratedb_grammar(version='master'):
    """
    Downloads CrateDB's `version` grammar files.

    Version should match a tag; for a list of tags run:
        $ curl https://api.github.com/repos/crate/crate/tags | jq -r '.[] | .name'
    """
    for file in build_options['files']:
        response = requests.get(file['url'].format(version=version))

        # We annotate the CrateDB branch and date of download to the Grammar files for reference.
        text = f'/* crate_branch={version}, at={datetime.datetime.now()}, annotatedby=cratedb_sqlparse */\n' + response.text

        with open(str(PARSER_COMPILE_PATH.parent / file['filename']), 'w') as f:
            f.write(text)


def compile_grammar(target: Antlr4Target):
    """
    Compiles antlr4 files into `target` code.
    """

    base_dir = build_options['antlr4_compiled_target_output'][target]
    sub_dir = build_options['antlr4_compiled_target_subdir']

    for file in build_options['files']:
        subprocess.run(
            [
                'antlr4', f'-Dlanguage={target.value}',
                '-o',
                str(PARSER_COMPILE_PATH / base_dir / sub_dir),
                file['filename']
            ]
        )


def patch_lexer(target: Antlr4Target):
    """
    Patches the lexer file, removing bad syntax generated by Antlr4.
    """

    REMOVE_LINES = [
        'import io.crate.sql.AbstractSqlBaseLexer;',
    ]

    # If more targets are added, this needs to be improved.
    extension = 'py' if target == Antlr4Target.python else 'js'

    base_dir = build_options['antlr4_compiled_target_output'][target]
    sub_dir = build_options['antlr4_compiled_target_subdir']
    file_name = build_options['files'][0]['filename'].replace('g4', extension)

    lexer_file = PARSER_COMPILE_PATH / base_dir / sub_dir / file_name

    text = pathlib.Path(lexer_file).read_text()

    for text_to_remove in REMOVE_LINES:
        text = text.replace(text_to_remove, '')

    pathlib.Path(lexer_file).write_text(text)


def set_version(target: Antlr4Target, version: str):
    """
    Specifies the compiled version to the target package,
    depending on the package the strategy differs.
    """
    base_dir = build_options['antlr4_compiled_target_output'][target]
    sub_dir = build_options['antlr4_compiled_target_subdir']

    target_path = (PARSER_COMPILE_PATH / base_dir / sub_dir).parent

    version = f'"{version}"'  # Escape quotes on echo command.

    index_file = ''
    variable = ''

    if target == Antlr4Target.python:
        index_file = '__init__.py'
        variable = '__cratedb_version__'

    if target == Antlr4Target.js:
        index_file = 'index.js'
        variable = 'export const __cratedb_version__'

    with open(target_path / index_file, "a") as f:
        f.write(f"{variable} = {version}\n")

# if __name__ == '__main__':
#     download_cratedb_grammar('5.6.4')
#     compile_grammar(Antlr4Target.js)
#     patch_lexer(Antlr4Target.js)
set_version(Antlr4Target.js, '5.45.4')
