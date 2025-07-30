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
