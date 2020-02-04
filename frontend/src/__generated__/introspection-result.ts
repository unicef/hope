
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
            "name": "CashPlanNode"
          },
          {
            "name": "ProgramNode"
          },
          {
            "name": "LocationNode"
          },
          {
            "name": "BusinessAreaNode"
          },
          {
            "name": "RegistrationDataImportNode"
          },
          {
            "name": "HouseholdNode"
          },
          {
            "name": "TargetPopulationNode"
          }
        ]
      }
    ]
  }
};
      export default result;
    