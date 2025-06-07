import fs from 'fs';
import yaml from 'js-yaml';
import _ from 'lodash';

// Function to automatically discover all choice endpoints from the OpenAPI spec
async function discoverChoiceEndpoints() {
  try {
    const response = await fetch('http://localhost:8080/api/rest/');
    const openApiText = await response.text();
    const openApiSpec = yaml.load(openApiText);

    const choiceEndpoints = new Set();

    // Find all endpoints that match the pattern /api/rest/choices/{choice-type}/
    for (const [path, pathObj] of Object.entries(openApiSpec.paths || {})) {
      if (path.startsWith('/api/rest/choices/') && path.endsWith('/')) {
        const choiceType = path
          .replace('/api/rest/choices/', '')
          .replace('/', '');
        if (choiceType) {
          choiceEndpoints.add(choiceType);
        }
      }
    }

    console.log('Discovered choice endpoints:', Array.from(choiceEndpoints));
    return Array.from(choiceEndpoints);
  } catch (error) {
    console.warn(
      'Failed to discover choice endpoints, using fallback list:',
      error.message,
    );
    // Fallback to known endpoints
    return [
      'payment-plan-status',
      'payment-plan-background-action-status',
      'payment-record-delivery-type',
      'grievance-ticket-category',
      'grievance-ticket-status',
      'grievance-ticket-priority',
      'grievance-ticket-urgency',
      'grievance-ticket-issue-type',
    ];
  }
}

// Function to generate enum name from endpoint
function generateEnumName(endpoint) {
  return (
    endpoint
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join('') + 'Enum'
  );
}

// Function to find potential field mappings in schemas
function findFieldMappings(openApiSchema, enumName, endpoint) {
  const fields = [];

  // Extract the endpoint parts
  const endpointParts = endpoint.split('-');
  const lastConcept = endpointParts[endpointParts.length - 1]; // e.g., 'status' from 'payment-plan-status'

  // Create more specific field name patterns
  const patterns = [];

  // For payment-plan-status -> look for fields that contain both "payment" and "status"
  if (endpointParts.length > 1) {
    patterns.push(endpoint.replace(/-/g, '_')); // exact snake_case match
    patterns.push(_.camelCase(endpoint)); // exact camelCase match

    // If it ends with status/type/category, look for those specific patterns
    if (
      ['status', 'type', 'category', 'priority', 'urgency'].includes(
        lastConcept,
      )
    ) {
      patterns.push(lastConcept);

      // Also look for compound patterns like backgroundActionStatus for payment-plan-background-action-status
      if (endpointParts.length > 2) {
        const compound = endpointParts.slice(1).join('_'); // background_action_status
        const compoundCamel = _.camelCase(endpointParts.slice(1).join('-')); // backgroundActionStatus
        patterns.push(compound);
        patterns.push(compoundCamel);
      }
    }
  } else {
    // Single word endpoints like 'currencies'
    patterns.push(endpoint);
    patterns.push(_.camelCase(endpoint));
  }

  console.log(
    `Looking for field patterns for ${enumName} (${endpoint}):`,
    patterns,
  );

  for (const [schemaName, schema] of Object.entries(
    openApiSchema.components?.schemas || {},
  )) {
    if (schema.properties) {
      for (const [fieldName, fieldDef] of Object.entries(schema.properties)) {
        // Only consider string fields without format (which could be enums)
        if (fieldDef.type === 'string' && !fieldDef.format) {
          const fieldLower = fieldName.toLowerCase();
          const schemaLower = schemaName.toLowerCase();

          // Define mapping rules for specific endpoints
          const mappingRules = {
            'payment-plan-background-action-status': {
              requiredField: 'background_action_status',
              allowedSchemas: ['paymentplan', 'targetpopulation'],
            },
            'payment-plan-status': {
              requiredField: 'status',
              allowedSchemas: ['paymentplan', 'followuppaymentplan'],
            },
            'payment-verification-plan-status': {
              requiredField: 'status',
              allowedSchemas: ['paymentverification'],
            },
          };

          // Check if this endpoint has specific rules
          const rule = mappingRules[endpoint];
          if (rule) {
            // Apply specific rule
            if (fieldLower === rule.requiredField) {
              const matchesSchema = rule.allowedSchemas.some((allowedSchema) =>
                schemaLower.startsWith(allowedSchema),
              );
              if (matchesSchema) {
                fields.push(`${schemaName}.${fieldName}`);
              }
            }
            // Skip pattern matching for rule-based endpoints
            continue;
          }

          // Generic pattern matching for endpoints without specific rules
          let fieldMatched = false;
          for (const pattern of patterns) {
            const patternLower = pattern.toLowerCase();

            // Exact match first (highest priority)
            if (fieldLower === patternLower) {
              fields.push(`${schemaName}.${fieldName}`);
              fieldMatched = true;
              break;
            }

            // Partial matches for compound patterns
            if (pattern.includes('_') || pattern.includes('-')) {
              // For compound patterns, check if field contains all parts
              const patternParts = pattern.toLowerCase().split(/[_-]/);
              const fieldParts = fieldName.toLowerCase().split(/[_-]/);

              if (patternParts.every((part) => fieldParts.includes(part))) {
                fields.push(`${schemaName}.${fieldName}`);
                fieldMatched = true;
                break;
              }
            }
          }

          // Fallback: if last concept matches field name (for simple cases like 'status', 'type')
          if (
            !fieldMatched &&
            patterns.includes(lastConcept) &&
            fieldLower === lastConcept
          ) {
            // Only add if we don't have a more specific match already
            fields.push(`${schemaName}.${fieldName}`);
          }
        }
      }
    }
  }

  return [...new Set(fields)]; // Remove duplicates
}

async function fetchChoices() {
  const choices = {};
  const endpoints = await discoverChoiceEndpoints();

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(
        `http://localhost:8080/api/rest/choices/${endpoint}/`,
      );

      if (!response.ok) {
        console.warn(`Choice endpoint ${endpoint} returned ${response.status}`);
        continue;
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.warn(`Choice endpoint ${endpoint} returned non-JSON response`);
        continue;
      }

      const data = await response.json();

      // Validate that it's an array of choice objects
      if (!Array.isArray(data) || data.length === 0) {
        console.warn(
          `Choice endpoint ${endpoint} returned invalid data structure`,
        );
        continue;
      }

      // Validate choice structure
      const firstChoice = data[0];
      if (!firstChoice.value || !firstChoice.name) {
        console.warn(
          `Choice endpoint ${endpoint} returned invalid choice structure`,
        );
        continue;
      }

      const enumName = generateEnumName(endpoint);
      const enumValues = data.map((choice) => choice.value);

      choices[enumName] = {
        endpoint,
        values: enumValues,
        descriptions: data.reduce((acc, choice) => {
          acc[choice.value] = choice.name;
          return acc;
        }, {}),
      };

      console.log(
        `✓ Successfully fetched ${data.length} choices for ${endpoint} -> ${enumName}`,
      );
    } catch (error) {
      console.warn(`Failed to fetch choices for ${endpoint}:`, error.message);
    }
  }

  return choices;
}

function enhanceOpenApiWithEnums(openApiSchema, choices) {
  // Add enum schemas to components
  if (!openApiSchema.components) {
    openApiSchema.components = {};
  }
  if (!openApiSchema.components.schemas) {
    openApiSchema.components.schemas = {};
  }

  // Add enum definitions
  for (const [enumName, enumData] of Object.entries(choices)) {
    const description = Object.entries(enumData.descriptions)
      .map(([value, name]) => `* \`${value}\` - ${name}`)
      .join('\n');

    openApiSchema.components.schemas[enumName] = {
      enum: enumData.values,
      type: 'string',
      description: description,
    };
  }

  // Update field references to use enums (before camelizing)
  for (const [enumName, enumData] of Object.entries(choices)) {
    // Find field mappings for this enum
    const fieldMappings = findFieldMappings(
      openApiSchema,
      enumName,
      enumData.endpoint,
    );

    console.log(
      `Found ${fieldMappings.length} field mappings for ${enumName}:`,
      fieldMappings,
    );

    for (const fieldPath of fieldMappings) {
      const [schemaName, fieldName] = fieldPath.split('.');

      if (
        openApiSchema.components.schemas[schemaName] &&
        openApiSchema.components.schemas[schemaName].properties &&
        openApiSchema.components.schemas[schemaName].properties[fieldName]
      ) {
        // Replace string type with enum reference
        openApiSchema.components.schemas[schemaName].properties[fieldName] = {
          $ref: `#/components/schemas/${enumName}`,
        };
        console.log(`✓ Updated ${fieldPath} to use ${enumName}`);
      }
    }
  }

  return openApiSchema;
}

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

async function main() {
  try {
    console.log('Fetching choice data from API...');
    const choices = await fetchChoices();
    console.log('Fetched choices:', Object.keys(choices));

    console.log('Reading OpenAPI specification...');
    const fileContent = fs.readFileSync('data/openapi.yml', 'utf8');
    let openApiSchema = yaml.load(fileContent);

    console.log('Enhancing OpenAPI specification with enums...');
    openApiSchema = enhanceOpenApiWithEnums(openApiSchema, choices);

    // Debug: Check if enums were added
    console.log(
      'Added enum schemas:',
      Object.keys(openApiSchema.components.schemas).filter((name) =>
        name.includes('Enum'),
      ),
    );

    console.log('Camelizing OpenAPI specification...');
    for (let schemaName in openApiSchema.components.schemas) {
      if (!openApiSchema.components.schemas.hasOwnProperty(schemaName)) {
        continue;
      }

      if (openApiSchema.components.schemas[schemaName].properties) {
        openApiSchema.components.schemas[schemaName].properties =
          camelizeProperties(
            openApiSchema.components.schemas[schemaName].properties,
          );
      }

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

    console.log('Writing enhanced and camelized OpenAPI specification...');
    const enhancedYaml = yaml.dump(openApiSchema);
    fs.writeFileSync('data/openapi-camelcase.yml', enhancedYaml);

    console.log(
      'OpenAPI schema has been enhanced with enums and camelized successfully.',
    );
    console.log(`Added ${Object.keys(choices).length} enum definitions.`);
  } catch (error) {
    console.error('Error processing OpenAPI specification:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
}

main();
