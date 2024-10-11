import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from 'react';
import wait from 'waait';
import { IndividualsListTable } from '.';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllIndividualsForPopulationTable } from '../../../../../fixtures/population/fakeApolloAllIndividualsForPopulationTable';

describe('containers/tables/population/IndividualsListTable', () => {
  const initialFilter = {
    search: '',
    documentType: 'individual_id',
    documentNumber: '',
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
        <IndividualsListTable
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
        <IndividualsListTable
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
