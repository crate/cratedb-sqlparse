import pathlib
import subprocess
import requests

GRAMMAR = {
    'lexer': {
        'url': 'https://raw.githubusercontent.com/crate/crate/master/libs/sql-parser/src/main/antlr/io/crate/sql/parser/antlr/SqlBaseLexer.g4',
        'filename': 'SqlBaseLexer.g4'
    },
    'parser': {
        'url': 'https://raw.githubusercontent.com/crate/crate/master/libs/sql-parser/src/main/antlr/io/crate/sql/parser/antlr/SqlBaseParser.g4',
        'filename': 'SqlBaseParser.g4'
    }

}

PARSER_COMPILE_PATH = pathlib.Path(__file__).parent / 'cratedb-sqlparse/parser'


def download_cratedb_grammar():
    """
    Downloads CrateDB's grammar files.
    """
    for file in GRAMMAR.values():
        response = requests.get(file['url'])
        with open(str(pathlib.Path(__file__).parent / file['filename']),
                  'w') as f:
            f.write(response.text)


def compile_grammar():
    """
    Compiles antlr4 files into Python code.

    """
    for file in GRAMMAR.values():
        subprocess.run(
            ['antlr4', '-Dlanguage=Python3', '-o', str(PARSER_COMPILE_PATH), file['filename']]
        )


def patch_lexer():
    with open(PARSER_COMPILE_PATH / GRAMMAR['lexer']['filename'].replace('g4', 'py'), 'r+') as f:
        text = f.read()
        text = text.replace("""import io.crate.sql.AbstractSqlBaseLexer;""",
                            '#removed import - Modified automatically by cratedb-sqlparse')
        f.write(text)


patch_lexer()
