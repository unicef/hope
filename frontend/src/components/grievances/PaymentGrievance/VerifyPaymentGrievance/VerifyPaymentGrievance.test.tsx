import React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { render } from '../../../../testUtils/testUtils';
import { fakeApolloUpdateGrievanceDetailsPaymentVerificationMutation } from '../../../../../fixtures/grievances/fakeApolloUpdateGrievanceDetailsPaymentVerificationMutation';
import { fakeGrievanceTicketPaymentVerification } from '../../../../../fixtures/grievances/fakeGrievanceTicketPaymentVerification';
import { VerifyPaymentGrievance } from './VerifyPaymentGrievance';

describe('components/grievances/VerifyPaymentGrievance', () => {
  it('should render with data', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloUpdateGrievanceDetailsPaymentVerificationMutation}
      >
        <VerifyPaymentGrievance
          ticket={fakeGrievanceTicketPaymentVerification}
        />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
  });
});
