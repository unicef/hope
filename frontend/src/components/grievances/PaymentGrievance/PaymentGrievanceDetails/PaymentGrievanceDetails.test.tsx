import React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { render } from '../../../../testUtils/testUtils';
import { fakeApolloApprovePaymentDetailsMutation } from '../../../../../fixtures/grievances/fakeApolloApprovePaymentDetailsMutation';
import { fakeGrievanceTicketPaymentVerification } from '../../../../../fixtures/grievances/fakeGrievanceTicketPaymentVerification';
import { PaymentGrievanceDetails } from '.';

describe('components/grievances/PaymentGrievanceDetails', () => {
  it('should render with data', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloApprovePaymentDetailsMutation}
      >
        <PaymentGrievanceDetails
          /* eslint-disable-next-line @typescript-eslint/ban-ts-comment */
          /*@ts-ignore*/
          ticket={fakeGrievanceTicketPaymentVerification}
          canApprovePaymentVerification
        />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
  });
});
