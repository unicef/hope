import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloAllTargetPopulation } from '../../../../../fixtures/targeting/fakeApolloAllTargetPopulation';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { TargetPopulationTable } from '.';

describe('containers/tables/targeting/TargetPopulation/TargetPopulationTable', () => {
  const initialFilter = {
    name: '',
    status: '',
    program: '',
    numIndividualsMin: null,
    numIndividualsMax: null,
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllTargetPopulation}>
        <TargetPopulationTable filter={initialFilter} canViewDetails />
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
        <TargetPopulationTable filter={initialFilter} canViewDetails />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
