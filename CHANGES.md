# Changelog

## Unreleased
- Fix error matching issue when missing EOF

## 2024/10/25 v0.0.9
- Set CrateDB version to 5.8.3
- Fix error matching issue due to wrong error.query trimming in find_suitable_error

## 2024/10/16 v0.0.8
- Export `Statement` in both Python and Javascript target
- Fixed query parsing when expression includes special characters like `\n`, `\r`, or `\t`
- Fixed sqlparse crash on missing error context

## 2024/09/18 v0.0.7
- Improve error matching on single statements

## v0.0.6 skipped

## 2024/07/22 v0.0.5
- Add Table model, save all table references to metadata.tables
- Javascript: Fixing type declaration on export in package.json
- Javascript: Implement ExceptionCollectorListener and make it default behaviour

## 2024/07/02 v0.0.4
- Improve heuristics of assigning an error to its statement
- Add with_properties and interpolated_properties
- Extract metadata from the query into the statement

## v0.0.3 skipped

## 2024/05/21 v0.0.2
- Initial release
