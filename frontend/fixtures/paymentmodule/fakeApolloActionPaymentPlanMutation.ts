import { ActionPpDocument, Action } from '../../src/__generated__/graphql';


export const fakeActionPpMutation = [
  {
    request: {
      query: ActionPpDocument,
      variables: {
        input: {
          paymentPlanId: 'UGF5bWVudFBsYW5Ob2RlOmRiNWYxNDM4LTdjMTYtNDBmYi1iMzlmLTYwYTlmOGM3ZDkzNg==',
          action: Action.Approve,
          comment: 'fake comment',
        },
      },
    },
    result: {
      data: {
        paymentPlan: {
          id: 'UGF5bWVudFBsYW5Ob2RlOmRiNWYxNDM4LTdjMTYtNDBmYi1iMzlmLTYwYTlmOGM3ZDkzNg==',
          status: 'status',
        },
      },
    },
  },
];
