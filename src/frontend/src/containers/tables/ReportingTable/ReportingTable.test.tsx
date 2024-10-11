import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import * as React from 'react';
import wait from 'waait';
import { ReportingTable } from '.';
import { fakeApolloAllReports } from '../../../../fixtures/reporting/fakeApolloAllReports';
import { fakeReportChoiceData } from '../../../../fixtures/reporting/fakeReportChoiceData';
import { fakeMe } from '../../../../fixtures/core/fakeMe';
import { render } from '../../../testUtils/testUtils';

describe('containers/tables/ReportingTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllReports}>
        <ReportingTable
          businessArea="afghanistan"
          filter={{}}
          choicesData={fakeReportChoiceData}
          meData={fakeMe}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllReports}>
        <ReportingTable
          businessArea="afghanistan"
          filter={{}}
          choicesData={fakeReportChoiceData}
          meData={fakeMe}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
