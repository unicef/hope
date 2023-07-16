import { gql } from 'apollo-boost';

export const FeedbackIssueTypeChoices = gql`
  query FeedbackIssueTypeChoices {
    feedbackIssueTypeChoices {
      name
      value
    }
  }
`;
