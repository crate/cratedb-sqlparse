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

PARSER_COMPILE_PATH = pathlib.Path(__file__).parent / 'cratedb_sqlparse/parser/generated_parser'


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
    REMOVE_LINES = [
        'import io.crate.sql.AbstractSqlBaseLexer;',
        ]
    sqlbaselexer_pyfile = PARSER_COMPILE_PATH / GRAMMAR['lexer']['filename'].replace('g4', 'py')
    text = pathlib.Path(sqlbaselexer_pyfile).read_text()

    # We remove lines that do not properly work.
    for text_to_remove in REMOVE_LINES:
        text = text.replace(text_to_remove, '# Code removed by cratedb_sqlparse.setup_grammar.patch_lexer')

    pathlib.Path(sqlbaselexer_pyfile).write_text(text)


if __name__ == '__main__':
    download_cratedb_grammar()
    compile_grammar()
    patch_lexer()
