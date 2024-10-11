import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from 'react';
import wait from 'waait';
import { ImportedIndividualsTable } from '.';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllImportedIndividuals } from '../../../../../fixtures/registration/fakeApolloAllImportedIndividuals';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';

describe('containers/tables/rdi/ImportedIndividualsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllImportedIndividuals}>
        <ImportedIndividualsTable
          isMerged={false}
          businessArea="afghanistan"
          choicesData={fakeHouseholdChoices}
          rdiId="UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl"
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllImportedIndividuals}>
        <ImportedIndividualsTable
          isMerged={false}
          businessArea="afghanistan"
          choicesData={fakeHouseholdChoices}
          rdiId="UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl"
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
