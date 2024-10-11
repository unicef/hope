import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from 'react';
import wait from 'waait';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllCashPlansAndPaymentPlans } from '../../../../../fixtures/payments/fakeApolloAllCashPlansAndPaymentPlansForProgram';
import { fakeProgram } from '../../../../../fixtures/programs/fakeProgram';
import { CashPlanTable } from '.';

describe('containers/tables/payments/CashPlanTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCashPlansAndPaymentPlans}
      >
        <CashPlanTable program={fakeProgram} />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCashPlansAndPaymentPlans}
      >
        <CashPlanTable program={fakeProgram} />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
