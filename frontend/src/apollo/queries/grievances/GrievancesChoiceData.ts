import { gql } from '@apollo/client';

export const GrievancesChoiceData = gql`
  query GrievancesChoiceData {
    grievanceTicketStatusChoices {
      name
      value
    }

    grievanceTicketCategoryChoices {
      name
      value
    }

    grievanceTicketManualCategoryChoices {
      name
      value
    }

    grievanceTicketSystemCategoryChoices {
      name
      value
    }

    grievanceTicketPriorityChoices {
      name
      value
    }

    grievanceTicketUrgencyChoices {
      name
      value
    }

    grievanceTicketIssueTypeChoices {
      category
      label
      subCategories {
        name
        value
      }
    }

    grievanceTicketSearchTypesChoices {
      name
      value
    }
  }
`;
