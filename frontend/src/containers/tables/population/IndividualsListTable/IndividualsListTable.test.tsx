import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { IndividualsListTable } from '.';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllIndividualsForPopulationTable } from '../../../../../fixtures/population/fakeApolloAllIndividualsForPopulationTable';

describe('containers/tables/population/IndividualsListTable', () => {
  const initialFilter = {
    ageMin: '',
    ageMax: '',
    businessArea: 'afghanistan',
    sex: '',
    search: '',
    admin2: '',
    flags: [],
    status: '',
    lastRegistrationDateMin: '',
    lastRegistrationDateMax: '',
    orderBy: 'unicef_id',
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllIndividualsForPopulationTable}
      >
        <IndividualsListTable
          businessArea='afghanistan'
          filter={initialFilter}
          canViewDetails={true}
          choicesData={fakeHouseholdChoices}
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
        mocks={fakeApolloAllIndividualsForPopulationTable}
      >
        <IndividualsListTable
          businessArea='afghanistan'
          filter={initialFilter}
          canViewDetails={true}
          choicesData={fakeHouseholdChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
