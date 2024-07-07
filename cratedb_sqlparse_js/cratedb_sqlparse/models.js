/**
 * Represents the metadata of the query, the actual interesting parts of the query such as:
 * table, schema, columns, options...
 */
export class Metadata {

    /**
     * @param {Table[]} tables - The referenced tables in the query.
     * @param {object} parameterizedProperties - The properties whose value can be used to inject parameters, they start with '$', example: `CREATE TABLE a (b text) WITH ("allocation.max_retries" = $1)`
     * @param {object} withProperties - SQL properties, defined after a `WITH` statement. Example: `CREATE TABLE a (b text) WITH ("allocation.max_retries" = 5)`
     */
    constructor(tables, parameterizedProperties, withProperties) {
        this.tables = tables || []
        this.parameterizedProperties = parameterizedProperties || {}
        this.withProperties = withProperties || {}
    }
}

/**
 *
 * @param {string} text
 * @param {string} quoted_with
 * @return {string}
 */
function quoted(text, quoted_with = '"') {
    return quoted_with + text + quoted_with
}

export class Table {
    /**
     *
     * @param {string} name
     * @param {string} schema
     * @property {string} fqn - Full qualified name, example: "sys"."shards"
     */
    constructor(name, schema) {
        this.name = name
        this.schema = schema
        this.fqn = this._getFqn()
    }

    /**
     * @return {string} - The full qualified name, quoted.
     */
    _getFqn() {
        return (this.schema ? quoted(this.schema) + "." : "") + quoted(this.name)
    }
}