
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
            "name": "CommunicationMessageNode"
          },
          {
            "name": "UserNode"
          },
          {
            "name": "GrievanceTicketNode"
          },
          {
            "name": "AreaNode"
          },
          {
            "name": "AreaTypeNode"
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
            "name": "RuleCommitNode"
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
            "name": "CashPlanPaymentVerificationSummaryNode"
          },
          {
            "name": "TicketComplaintDetailsNode"
          },
          {
            "name": "TicketSensitiveDetailsNode"
          },
          {
            "name": "PaymentVerificationLogEntryNode"
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
            "name": "TicketNeedsAdjudicationDetailsNode"
          },
          {
            "name": "TicketPositiveFeedbackDetailsNode"
          },
          {
            "name": "TicketNegativeFeedbackDetailsNode"
          },
          {
            "name": "TicketReferralDetailsNode"
          },
          {
            "name": "DocumentNode"
          },
          {
            "name": "IndividualIdentityNode"
          },
          {
            "name": "BankAccountInfoNode"
          },
          {
            "name": "TicketHouseholdDataUpdateDetailsNode"
          },
          {
            "name": "TicketAddIndividualDetailsNode"
          },
          {
            "name": "TicketDeleteHouseholdDetailsNode"
          },
          {
            "name": "TicketNoteNode"
          },
          {
            "name": "CommunicationMessageRecipientMapNode"
          },
          {
            "name": "LogEntryNode"
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
            "name": "KoboImportDataNode"
          },
          {
            "name": "ImportedDocumentNode"
          },
          {
            "name": "ImportedIndividualIdentityNode"
          }
        ]
      }
    ]
  }
};
      export default result;
    