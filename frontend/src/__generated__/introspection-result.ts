
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
            "name": "SanctionListIndividualNode"
          },
          {
            "name": "TicketSystemFlaggingDetailsNode"
          },
          {
            "name": "IndividualNode"
          },
          {
            "name": "HouseholdNode"
          },
          {
            "name": "AdminAreaNode"
          },
          {
            "name": "AdminAreaTypeNode"
          },
          {
            "name": "UserBusinessAreaNode"
          },
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
            "name": "TargetPopulationNode"
          },
          {
            "name": "UserNode"
          },
          {
            "name": "GrievanceTicketNode"
          },
          {
            "name": "TicketNoteNode"
          },
          {
            "name": "TicketComplaintDetailsNode"
          },
          {
            "name": "TicketSensitiveDetailsNode"
          },
          {
            "name": "TicketHouseholdDataUpdateDetailsNode"
          },
          {
            "name": "TicketIndividualDataUpdateDetailsNode"
          },
          {
            "name": "TicketAddIndividualDetailsNode"
          },
          {
            "name": "TicketDeleteIndividualDetailsNode"
          },
          {
            "name": "TicketNeedsAdjudicationDetailsNode"
          },
          {
            "name": "TicketPaymentVerificationDetailsNode"
          },
          {
            "name": "PaymentVerificationNode"
          },
          {
            "name": "CashPlanPaymentVerificationNode"
          },
          {
            "name": "RegistrationDataImportNode"
          },
          {
            "name": "SteficonRuleNode"
          },
          {
            "name": "ServiceProviderNode"
          },
          {
            "name": "DocumentNode"
          },
          {
            "name": "SanctionListIndividualDocumentNode"
          },
          {
            "name": "SanctionListIndividualNationalitiesNode"
          },
          {
            "name": "SanctionListIndividualCountriesNode"
          },
          {
            "name": "SanctionListIndividualAliasNameNode"
          },
          {
            "name": "SanctionListIndividualDateOfBirthNode"
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
    