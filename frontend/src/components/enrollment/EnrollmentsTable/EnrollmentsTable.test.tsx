import { MockedProvider } from '@apollo/react-testing';
import { act, render } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { EnrollmentsTable } from '.';
import { fakeApolloAllTargetPopulation } from '../../../../fixtures/targeting/fakeApolloAllTargetPopulation';
import { ApolloLoadingLink } from '../../../testUtils/testUtils';

describe('components/enrollment/EnrollmentsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllTargetPopulation}>
        {/* <MockedProvider addTypename={false} mocks={fakeApolloAllEnrollments}> */}
        <EnrollmentsTable
          filter={{
            name: null,
            status: null,
            numHouseholds: { min: 0, max: 100 },
            numIndividuals: { min: 0, max: 100 },
          }}
          canViewDetails
        />
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
        mocks={fakeApolloAllTargetPopulation}
      >
        {/* <MockedProvider addTypename={false} mocks={fakeApolloAllEnrollments}> */}
        <EnrollmentsTable
          filter={{
            name: null,
            status: null,
            numHouseholds: { min: 0, max: 100 },
            numIndividuals: { min: 0, max: 100 },
          }}
          canViewDetails
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
