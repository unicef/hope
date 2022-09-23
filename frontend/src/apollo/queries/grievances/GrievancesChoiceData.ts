import { gql } from 'apollo-boost';

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
  }
`;
