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

    grievanceTicketSubCategoryChoices {
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
