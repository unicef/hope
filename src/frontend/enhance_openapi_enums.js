import fs from 'fs';
import yaml from 'js-yaml';

// Mapping of choice endpoints to their corresponding enum names and field paths
const CHOICE_MAPPINGS = {
  // 'payment-plan-status': {
  //   enumName: 'PaymentPlanStatusEnum',
  //   fields: ['PaymentPlan.status', 'FollowUpPaymentPlan.status'],
  // },
  'payment-plan-background-action-status': {
    enumName: 'PaymentPlanBackgroundActionStatusEnum',
    fields: ['PaymentPlanBulkAction.status'],
  },
  'payment-record-delivery-type': {
    enumName: 'PaymentRecordDeliveryTypeEnum',
    fields: ['PaymentDetail.delivery_type', 'PaymentList.delivery_type'],
  },
  // Add more mappings as needed
};

async function fetchChoices() {
  const choices = {};

  for (const [endpoint, config] of Object.entries(CHOICE_MAPPINGS)) {
    try {
      const response = await fetch(
        `http://localhost:8080/api/rest/choices/${endpoint}/`,
      );
      const data = await response.json();

      // Convert choice data to enum values
      const enumValues = data.map((choice) => choice.value);
      choices[config.enumName] = {
        values: enumValues,
        descriptions: data.reduce((acc, choice) => {
          acc[choice.value] = choice.name;
          return acc;
        }, {}),
      };
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

  // Update field references to use enums
  for (const [endpoint, config] of Object.entries(CHOICE_MAPPINGS)) {
    if (!choices[config.enumName]) continue;

    for (const fieldPath of config.fields) {
      const [schemaName, fieldName] = fieldPath.split('.');

      if (
        openApiSchema.components.schemas[schemaName] &&
        openApiSchema.components.schemas[schemaName].properties &&
        openApiSchema.components.schemas[schemaName].properties[fieldName]
      ) {
        // Replace string type with enum reference
        openApiSchema.components.schemas[schemaName].properties[fieldName] = {
          $ref: `#/components/schemas/${config.enumName}`,
        };
      }
    }
  }

  return openApiSchema;
}

async function main() {
  try {
    console.log('Fetching choice data from API...');
    const choices = await fetchChoices();
    console.log('Fetched choices:', Object.keys(choices));

    console.log('Reading OpenAPI specification...');
    const fileContent = fs.readFileSync('data/openapi.yml', 'utf8');
    const openApiSchema = yaml.load(fileContent);

    console.log('Enhancing OpenAPI specification with enums...');
    const enhancedSchema = enhanceOpenApiWithEnums(openApiSchema, choices);

    console.log('Writing enhanced OpenAPI specification...');
    const enhancedYaml = yaml.dump(enhancedSchema);
    fs.writeFileSync('data/openapi-enhanced.yml', enhancedYaml);

    console.log(
      'OpenAPI specification has been enhanced with enum definitions.',
    );
    console.log(`Added ${Object.keys(choices).length} enum definitions.`);
  } catch (error) {
    console.error('Error enhancing OpenAPI specification:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
}

main();
