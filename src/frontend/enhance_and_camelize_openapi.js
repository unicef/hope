import fs from 'fs';
import yaml from 'js-yaml';
import _ from 'lodash';

const NEWLINE_RE = /[\r\n]/g;
const CHOICES_FILE = 'data/choices.json';

const EXCLUDED_CHOICE_ENDPOINTS = [
  'payment-record-delivery-type',
];

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
            'grievance-ticket-category': {
              requiredField: 'category',
              allowedSchemas: ['grievanceticket'],
            },
            'grievance-ticket-status': {
              requiredField: 'status',
              allowedSchemas: ['grievanceticket'],
            },
            'grievance-ticket-priority': {
              requiredField: 'priority',
              allowedSchemas: ['grievanceticket'],
            },
            'grievance-ticket-urgency': {
              requiredField: 'urgency',
              allowedSchemas: ['grievanceticket'],
            },
            'grievance-ticket-issue-type': {
              requiredField: 'issue_type',
              allowedSchemas: ['grievanceticket'],
            },
            'payment-record-delivery-type': {
              requiredField: 'delivery_type',
              allowedSchemas: ['paymentrecord', 'payment'],
            },
            'feedback-issue-type': {
              requiredField: 'issue_type',
              allowedSchemas: ['feedback'],
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
            // Skip all other pattern matching for rule-based endpoints
            continue;
          }

          // For endpoints without specific rules, be more restrictive
          // Only match if the endpoint is very generic (single word) or if we have exact matches
          if (endpointParts.length === 1) {
            // Single word endpoints like 'currencies' - allow exact matches only
            if (
              fieldLower === endpoint.toLowerCase() ||
              fieldLower === _.camelCase(endpoint)
            ) {
              fields.push(`${schemaName}.${fieldName}`);
            }
          } else {
            // Multi-part endpoints - require exact compound matches, not just the last part
            const exactSnakeCase = endpoint.replace(/-/g, '_');
            const exactCamelCase = _.camelCase(endpoint);

            if (
              fieldLower === exactSnakeCase ||
              fieldLower === exactCamelCase
            ) {
              fields.push(`${schemaName}.${fieldName}`);
            }
          }
        }
      }
    }
  }

  return [...new Set(fields)]; // Remove duplicates
}

function loadChoices() {
  const choices = {};

  if (!fs.existsSync(CHOICES_FILE)) {
    throw new Error(
      `Choices file ${CHOICES_FILE} not found. Run \`uv run python manage.py generate_openapi\` first.`,
    );
  }

  const choicesByEndpoint = JSON.parse(fs.readFileSync(CHOICES_FILE, 'utf8'));

  for (const [endpoint, data] of Object.entries(choicesByEndpoint)) {
    if (EXCLUDED_CHOICE_ENDPOINTS.includes(endpoint)) {
      console.log(`Skipping enum generation for ${endpoint}`);
      continue;
    }

    // Validate that it's an array of choice objects
    if (!Array.isArray(data) || data.length === 0) {
      console.warn(`Choice endpoint ${endpoint} has invalid data structure`);
      continue;
    }

    // Validate choice structure
    const firstChoice = data[0];
    if (!firstChoice.value || !firstChoice.name) {
      console.warn(`Choice endpoint ${endpoint} has invalid choice structure`);
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
      `✓ Loaded ${data.length} choices for ${String(endpoint).replace(NEWLINE_RE, '')} -> ${String(enumName).replace(NEWLINE_RE, '')}`,
    );
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
    console.log('Loading choice data from file...');
    const choices = loadChoices();
    console.log('Loaded choices:', Object.keys(choices));

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
