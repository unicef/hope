import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { TargetPopulationTable } from '.';
import { fakeApolloAllTargetPopulation } from '../../../../../fixtures/targeting/fakeApolloAllTargetPopulation';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/targeting/TargetPopulation/TargetPopulationTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllTargetPopulation}>
        <TargetPopulationTable
          filter={{
            name: null,
            numIndividuals: { min: 0, max: 100 },
            status: null,
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
        <TargetPopulationTable
          filter={{
            name: null,
            numIndividuals: { min: 0, max: 100 },
            status: null,
          }}
          canViewDetails
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
