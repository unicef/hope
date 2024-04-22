import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { PeopleListTable } from '.';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllIndividualsForPopulationTable } from '../../../../../fixtures/population/fakeApolloAllIndividualsForPopulationTable';

describe('containers/tables/population/PeopleListTable', () => {
  const initialFilter = {
    search: '',
    searchType: 'individual_id',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
    status: '',
    lastRegistrationDateMin: '',
    lastRegistrationDateMax: '',
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllIndividualsForPopulationTable}
      >
        <PeopleListTable
          businessArea="afghanistan"
          filter={initialFilter}
          canViewDetails
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
        addTypename={false}
        mocks={fakeApolloAllIndividualsForPopulationTable}
      >
        <PeopleListTable
          businessArea="afghanistan"
          filter={initialFilter}
          canViewDetails
          choicesData={fakeHouseholdChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
