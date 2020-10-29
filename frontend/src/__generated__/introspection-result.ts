
      export interface IntrospectionResultData {
        __schema: {
          types: {
            kind: string;
            name: string;
            possibleTypes: {
              name: string;
            }[];
          }[];
        };
      }
      const result: IntrospectionResultData = {
  "__schema": {
    "types": [
      {
        "kind": "INTERFACE",
        "name": "Node",
        "possibleTypes": [
          {
            "name": "SteficonRuleNode"
          },
          {
            "name": "TargetPopulationNode"
          },
          {
            "name": "UserNode"
          },
          {
            "name": "UserBusinessAreaNode"
          },
          {
            "name": "HouseholdNode"
          },
          {
            "name": "AdminAreaNode"
          },
          {
            "name": "ProgramNode"
          },
          {
            "name": "CashPlanNode"
          },
          {
            "name": "PaymentRecordNode"
          },
          {
            "name": "ServiceProviderNode"
          },
          {
            "name": "PaymentVerificationNode"
          },
          {
            "name": "CashPlanPaymentVerificationNode"
          },
          {
            "name": "IndividualNode"
          },
          {
            "name": "RegistrationDataImportNode"
          },
          {
            "name": "DocumentNode"
          },
          {
            "name": "BusinessAreaNode"
          },
          {
            "name": "ImportedHouseholdNode"
          },
          {
            "name": "ImportedIndividualNode"
          },
          {
            "name": "RegistrationDataImportDatahubNode"
          },
          {
            "name": "ImportDataNode"
          },
          {
            "name": "ImportedDocumentNode"
          }
        ]
      }
    ]
  }
};
      export default result;
    