import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllCashPlans } from '../../../../../fixtures/payments/fakeApolloAllCashPlans';
import { fakeProgram } from '../../../../../fixtures/programs/fakeProgram';
import { CashPlanTable } from '.';

describe('containers/tables/payments/CashPlanTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllCashPlans}>
        <CashPlanTable program={fakeProgram} />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        link={new ApolloLoadingLink()}
        addTypename={false}
        mocks={fakeApolloAllCashPlans}
      >
        <CashPlanTable program={fakeProgram} />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
