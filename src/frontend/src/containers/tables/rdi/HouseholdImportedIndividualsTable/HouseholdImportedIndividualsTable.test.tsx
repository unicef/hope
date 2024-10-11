import * as React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { HouseholdImportedIndividualsTable } from '.';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeImportedHouseholdNode } from '../../../../../fixtures/registration/fakeImportedHouseholdNode';
import { fakeApolloMe } from '../../../../../fixtures/core/fakeApolloMe';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/rdi/HouseholdImportedIndividualsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloMe}>
        <HouseholdImportedIndividualsTable
          household={fakeImportedHouseholdNode}
          choicesData={fakeHouseholdChoices}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloMe}>
        <HouseholdImportedIndividualsTable
          household={fakeImportedHouseholdNode}
          choicesData={fakeHouseholdChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
