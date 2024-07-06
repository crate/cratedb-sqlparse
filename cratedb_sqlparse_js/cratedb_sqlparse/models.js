/**
 * Represents the metadata of the query, the actual interesting parts of the query such as:
 * table, schema, columns, options...
 */
export class Metadata {

    /**
     *
     * @param {Table[]} tables
     * @param parameterizedProperties
     * @param withProperties
     */
    constructor(tables, parameterizedProperties, withProperties) {
        this.tables = tables || []
        this.parameterizedProperties = parameterizedProperties || {}
        this.withProperties = withProperties || {}
    }

    toString() {

    }
}

/**
 *
 * @param {String} text
 * @param {String} quoted_with
 */
function quoted(text, quoted_with = '"') {
    return quoted_with + text + quoted_with
}

export class Table {
    /**
     *
     * @param {String} name
     * @param {String} schema
     */
    constructor(name, schema) {
        this.name = name
        this.schema = schema
        this.fqn = this._getFqn()
    }

    /**
     * @return {String} The full qualified name, quoted.
     */
    _getFqn() {
        return (this.schema ? quoted(this.schema) + "." : "") + quoted(this.name)
    }
}