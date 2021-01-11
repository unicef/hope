
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
            "name": "ReportNode"
          },
          {
            "name": "UserBusinessAreaNode"
          },
          {
            "name": "AdminAreaTypeNode"
          },
          {
            "name": "AdminAreaNode"
          },
          {
            "name": "HouseholdNode"
          },
          {
            "name": "IndividualNode"
          },
          {
            "name": "RegistrationDataImportNode"
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
            "name": "SteficonRuleNode"
          },
          {
            "name": "CashPlanPaymentVerificationNode"
          },
          {
            "name": "PaymentVerificationNode"
          },
          {
            "name": "TicketPaymentVerificationDetailsNode"
          },
          {
            "name": "ServiceProviderNode"
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
            "name": "TicketSystemFlaggingDetailsNode"
          },
          {
            "name": "SanctionListIndividualNode"
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
            "name": "TicketNeedsAdjudicationDetailsNode"
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
    