import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { ImportedHouseholdTable } from '.';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllImportedHouseholds } from '../../../../../fixtures/registration/fakeApolloAllImportedHouseholds';
import { fakeRegistrationDetailedFragment } from '../../../../../fixtures/registration/fakeRegistrationDetailedFragment';

describe('containers/tables/rdi/ImportedHouseholdTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllImportedHouseholds}>
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
      <MockedProvider
        link={new ApolloLoadingLink()}
        mocks={fakeApolloAllImportedHouseholds}
      >
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
