import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import { fakeApolloAllTargetPopulation } from '../../../../../fixtures/targeting/fakeApolloAllTargetPopulation';
import wait from 'waait';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { TargetPopulationForPeopleTable } from '.';

describe('containers/tables/targeting/TargetPopulation/TargetPopulationTable', () => {
  const initialFilter = {
    name: '',
    status: '',
    totalHouseholdsCountMin: null,
    totalHouseholdsCountMax: null,
    createdAtRangeMin: '',
    createdAtRangeMax: '',
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllTargetPopulation}>
        <TargetPopulationForPeopleTable filter={initialFilter} canViewDetails />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllTargetPopulation}>
        <TargetPopulationForPeopleTable filter={initialFilter} canViewDetails />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
