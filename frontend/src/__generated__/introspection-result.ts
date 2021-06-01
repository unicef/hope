
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
            "name": "LogEntryNode"
          },
          {
            "name": "UserNode"
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
            "name": "GrievanceTicketNode"
          },
          {
            "name": "RegistrationDataImportNode"
          },
          {
            "name": "HouseholdNode"
          },
          {
            "name": "IndividualNode"
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
            "name": "ReportNode"
          },
          {
            "name": "ServiceProviderNode"
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
            "name": "TicketComplaintDetailsNode"
          },
          {
            "name": "TicketSensitiveDetailsNode"
          },
          {
            "name": "TicketIndividualDataUpdateDetailsNode"
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
            "name": "DocumentNode"
          },
          {
            "name": "TicketHouseholdDataUpdateDetailsNode"
          },
          {
            "name": "TicketAddIndividualDetailsNode"
          },
          {
            "name": "TicketNoteNode"
          },
          {
            "name": "TicketNeedsAdjudicationDetailsNode"
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
    