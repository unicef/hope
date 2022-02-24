import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { IndividualsListTable } from '.';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllIndividuals } from '../../../../../fixtures/population/fakeApolloAllIndividuals';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';

describe('containers/tables/population/IndividualsListTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllIndividuals}>
        <IndividualsListTable
          businessArea='afghanistan'
          filter={{}}
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
        mocks={fakeApolloAllIndividuals}
      >
        <IndividualsListTable
          businessArea='afghanistan'
          filter={{}}
          canViewDetails={true}
          choicesData={fakeHouseholdChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
