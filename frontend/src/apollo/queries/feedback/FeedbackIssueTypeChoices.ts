import { gql } from '@apollo/client';

export const FeedbackIssueTypeChoices = gql`
  query FeedbackIssueTypeChoices {
    feedbackIssueTypeChoices {
      name
      value
    }
  }
`;
