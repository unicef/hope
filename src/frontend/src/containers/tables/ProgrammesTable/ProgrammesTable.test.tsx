import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from 'react';
import wait from 'waait';
import { ProgrammesTable } from '.';
import { render } from '../../../testUtils/testUtils';
import { fakeProgramChoices } from '../../../../fixtures/programs/fakeProgramChoices';
import { fakeApolloAllPrograms } from '../../../../fixtures/programs/fakeApolloAllPrograms';

describe('containers/tables/ProgrammesTable', () => {
  const initialFilter = {
    search: '',
    startDate: '',
    endDate: '',
    status: '',
    sector: [],
    numberOfHouseholdsMin: '',
    numberOfHouseholdsMax: '',
    budgetMin: '',
    budgetMax: '',
    dataCollectingType: '',
  };

  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPrograms}>
        <ProgrammesTable
          businessArea="afghanistan"
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
      <MockedProvider addTypename={false} mocks={fakeApolloAllPrograms}>
        <ProgrammesTable
          businessArea="afghanistan"
          filter={initialFilter}
          choicesData={fakeProgramChoices}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
