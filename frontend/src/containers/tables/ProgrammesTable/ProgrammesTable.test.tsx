import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from '@testing-library/react';
import wait from 'waait';
import { ProgrammesTable } from '.';
import { render, ApolloLoadingLink } from '../../../testUtils/testUtils';
import { fakeProgramChoices } from '../../../../fixtures/programs/fakeProgramChoices';
import { fakeApolloAllPrograms } from '../../../../fixtures/programs/fakeApolloAllPrograms';

describe('containers/tables/ProgrammesTable', () => {
  const initialFilter = {
    search: '',
    startDate: undefined,
    endDate: undefined,
    status: '',
    sector: [],
    numberOfHouseholdsMin: '',
    numberOfHouseholdsMax: '',
    budgetMin: '',
    budgetMax: '',
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPrograms}>
        <ProgrammesTable
          businessArea='afghanistan'
          filter={initialFilter}
          choicesData={fakeProgramChoices}
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
        mocks={fakeApolloAllPrograms}
      >
        <ProgrammesTable
          businessArea='afghanistan'
          filter={initialFilter}
          choicesData={fakeProgramChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
