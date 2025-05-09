// const fs = require('fs');
// const yaml = require('js-yaml');
// const _ = require('lodash');
import fs from 'fs';
import yaml from 'js-yaml';
import _ from 'lodash';

function camelizeProperties(properties) {
  var newProperties = {};
  for (var key in properties) {
    if (!properties.hasOwnProperty(key)) {
      continue;
    }
    var newKey = _.camelCase(key);
    newProperties[newKey] = properties[key];
  }
  return newProperties;
}

// Read your OpenAPI YAML file
const fileContent = fs.readFileSync('data/openapi.yml', 'utf8');
const openApiSchema = yaml.load(fileContent);

for (let schemaName in openApiSchema.components.schemas) {
  if (!openApiSchema.components.schemas.hasOwnProperty(schemaName)) {
    continue;
  }

  openApiSchema.components.schemas[schemaName].properties = camelizeProperties(
    openApiSchema.components.schemas[schemaName].properties,
  );
  var required = openApiSchema.components.schemas[schemaName].required;
  if (!required) {
    continue;
  }
  var newRequired = [];
  for (let field of required) {
    newRequired.push(_.camelCase(field));
  }
  openApiSchema.components.schemas[schemaName].required = newRequired;
}

// Dump the transformed schema back to YAML
const newYaml = yaml.dump(openApiSchema);
fs.writeFileSync('data/openapi-camelcase.yml', newYaml);

console.log('OpenAPI schema has been camelized successfully.');
