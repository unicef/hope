
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
            "name": "PaymentRecordNode"
          },
          {
            "name": "BusinessAreaNode"
          },
          {
            "name": "UserNode"
          },
          {
            "name": "TargetPopulationNode"
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
            "name": "CashPlanPaymentVerificationNode"
          },
          {
            "name": "PaymentVerificationNode"
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
            "name": "ServiceProviderNode"
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
    