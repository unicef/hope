import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { PeopleListTable } from '.';
import { render } from '../../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllIndividualsForPopulationTable } from '../../../../../fixtures/population/fakeApolloAllIndividualsForPopulationTable';

describe('containers/tables/population/PeopleListTable', () => {
  const initialFilter = {
    search: '',
    documentType: 'national_id',
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
        <PeopleListTable
          businessArea="afghanistan"
          filter={initialFilter}
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
        addTypename={false}
        mocks={fakeApolloAllIndividualsForPopulationTable}
      >
        <PeopleListTable
          businessArea="afghanistan"
          filter={initialFilter}
          canViewDetails
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
