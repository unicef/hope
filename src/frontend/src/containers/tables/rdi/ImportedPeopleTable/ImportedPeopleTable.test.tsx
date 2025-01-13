import { MockedProvider } from '@apollo/react-testing';

import { act } from 'react';
import wait from 'waait';
import { ImportedPeopleTable } from '.';
import { render } from '../../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllIndividualsForPopulationTable } from '../../../../../fixtures/population/fakeApolloAllIndividualsForPopulationTable';

describe('containers/tables/rdi/ImportedIndividualsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllIndividualsForPopulationTable}>
        <ImportedPeopleTable
          isMerged={false}
          businessArea="afghanistan"
          choicesData={fakeHouseholdChoices}
          rdiId="UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl"
          rdi={{
            id: 'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl',
            name: 'Rdi Name',
          }}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllIndividualsForPopulationTable}>
        <ImportedPeopleTable
          isMerged={false}
          businessArea="afghanistan"
          choicesData={fakeHouseholdChoices}
          rdiId="UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl"
          rdi={{
            id: 'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl',
            name: 'Rdi Name',
          }}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
