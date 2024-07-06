import SqlBaseParserVisitor from "./generated_parser/SqlBaseParserVisitor.js";
import {Statement} from "./parser.js"
import {Table} from "./models.js"


/**
 *
 * @param {String} text
 * @returns {Boolean}
 */
function isDigit(text) {
    return text.split('').every(char => char >= '0' && char <= '9');
}


export class AstBuilder extends SqlBaseParserVisitor {
//     The class implements the antlr4 visitor pattern similar to how we do it in CrateDB
//     https://github.com/crate/crate/blob/master/libs/sql-parser/src/main/java/io/crate/sql/parser/AstBuilder.java
//
//     The biggest difference is that in CrateDB, `AstBuilder`, visitor methods
//     return a specialized Statement visitor.
//
//     Sqlparse just extracts whatever data it needs from the context and injects it to the current
//     visited statement, enriching its metadata.

    /**
     *
     * @param {Object} node
     * @returns {(String|null)}
     */
    getText(node){
        if(node){
            return node.getText().replaceAll("'", "").replaceAll('"', "")
        }
        return null
    }

    /**
     *
     * @param {Statement} stmt
     */
    enrich(stmt) {
        this.stmt = stmt
        this.visit(this.stmt.ctx)
    }

    /**
     *
     * @param {SqlBaseParser.TableNameContext} ctx
     */
    visitTableName(ctx) {
        const fqn = ctx.qname()
        const parts = this.getText(fqn).split(".")

        let schema = null
        let name = null;
        if (parts.length === 1){
            name = parts[0]
        } else {
            schema = parts[0]
            name = parts[1]
        }

        this.stmt.metadata.tables.push(
            new Table(name, schema)
        )
    }

    /**
     *
      * @param {SqlBaseParser.GenericPropertiesContext} ctx
     */
    visitGenericProperties(ctx) {
        const nodeProperties = ctx.genericProperty()
        const properties = {}
        const parameterizedProperties = {}

        for (const property of nodeProperties) {
            let key = this.getText(property.ident())
            let value = this.getText(property.expr())

            properties[key] = value

            if (value && value[0] === '$') {
                // It might be a parameterized value, e.g. '$1'
                if (isDigit(value.slice(1))) {
                    parameterizedProperties[key] = value
                }
            }

            this.stmt.metadata.withProperties = properties
            this.stmt.metadata.parameterizedProperties = parameterizedProperties

        }
    }

}