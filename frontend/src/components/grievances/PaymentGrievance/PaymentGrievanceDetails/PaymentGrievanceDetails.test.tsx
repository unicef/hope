import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { PaymentGrievanceDetails } from '.';
import { fakeApolloApprovePaymentDetailsMutation } from '../../../../../fixtures/grievances/fakeApolloApprovePaymentDetailsMutation';
import { fakeGrievanceTicketPaymentVerification } from '../../../../../fixtures/grievances/fakeGrievanceTicketPaymentVerification';
import { MockedProvider } from '@apollo/react-testing';

describe('components/grievances/PaymentGrievanceDetails', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloApprovePaymentDetailsMutation}
      >
        <PaymentGrievanceDetails
          ticket={fakeGrievanceTicketPaymentVerification}
          canApprovePaymentVerification
        />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
  });
});
