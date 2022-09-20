import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloAllCommunicationMessages } from '../../../../fixtures/communication/fakeApolloAllCommunicationMessages';
import { ApolloLoadingLink, render } from '../../../testUtils/testUtils';
import { CommunicationTable } from './CommunicationTable';

describe('containers/tables//Communication/CommunicationTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCommunicationMessages}
      >
        <CommunicationTable
          filter={{
            targetPopulation: '',
            createdBy: '',
            businessArea: 'afghanistan',
            first: 10,
            orderBy: '-created_at',
          }}
          businessArea={'afghanistan'}
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
        mocks={fakeApolloAllCommunicationMessages}
      >
        <CommunicationTable
          filter={{
            targetPopulation: '',
            createdBy: '',
            businessArea: 'afghanistan',
            first: 10,
            orderBy: '-created_at',
          }}
          businessArea={'afghanistan'}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
