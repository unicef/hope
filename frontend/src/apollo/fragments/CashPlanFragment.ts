import { graphql } from 'relay-runtime';

export const CashPlanFragment = graphql`
  fragment CashPlanFragment on ProgramNode {
    cashPlans(first: $count, after: $after)
      @connection(key: "CashPlanFragment_cashPlans") {
      edges {
        node {
          id
        }
      }
    }
  }
`;
