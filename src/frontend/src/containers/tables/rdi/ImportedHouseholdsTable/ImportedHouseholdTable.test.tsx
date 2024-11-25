import { MockedProvider } from '@apollo/react-testing';

import { act } from 'react';
import wait from 'waait';
import { ImportedHouseholdTable } from '.';
import { render } from '../../../../testUtils/testUtils';
import { fakeRegistrationDetailedFragment } from '../../../../../fixtures/registration/fakeRegistrationDetailedFragment';
import { fakeApolloAllHouseholdsForPopulationTable } from 'fixtures/population/fakeApolloAllHouseholdsForPopulationTable';

describe('containers/tables/rdi/ImportedHouseholdTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllHouseholdsForPopulationTable}>
        <ImportedHouseholdTable
          businessArea="afghanistan"
          rdi={fakeRegistrationDetailedFragment}
          isMerged={false}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllHouseholdsForPopulationTable}>
        <ImportedHouseholdTable
          businessArea="afghanistan"
          rdi={fakeRegistrationDetailedFragment}
          isMerged={false}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
