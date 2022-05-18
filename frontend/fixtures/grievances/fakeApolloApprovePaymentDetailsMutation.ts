import { ApprovePaymentDetailsDocument } from '../../src/__generated__/graphql';

export const fakeApolloApprovePaymentDetailsMutation = [
  {
    request: {
      query: ApprovePaymentDetailsDocument,
      variables: {
        approveStatus: false,
        grievanceTicketId:
          'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ZTY1N2JiZC1hNzM4LTQ0MTktYjlmOS04YTIyOWI2MGUwNzU',
      },
    },
    result: {
      data: {
        approvePaymentDetails: {
          grievanceTicket: {
            id:
              'R3JpZXZhbmNlVGlja2V0Tm9kZTo3ZTY1N2JiZC1hNzM4LTQ0MTktYjlmOS04YTIyOWI2MGUwNzU=',
            status: 5,
            paymentVerificationTicketDetails: {
              id:
                'VGlja2V0UGF5bWVudFZlcmlmaWNhdGlvbkRldGFpbHNOb2RlOmQ5NWFlNzA2LWRmNTQtNDYyMi1hODVmLTRiOGExZTg2Y2VhMQ==',
              approveStatus: false,
              __typename: 'TicketPaymentVerificationDetailsNode',
            },
            __typename: 'GrievanceTicketNode',
          },
          __typename: 'PaymentDetailsApproveMutation',
        },
      },
    },
  },
];
