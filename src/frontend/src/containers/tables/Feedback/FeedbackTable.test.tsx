import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';

import wait from 'waait';
import { fakeApolloAllFeedbacks } from '../../../../fixtures/feedback/fakeApolloAllFeedbacks';
import { render } from '../../../testUtils/testUtils';
import FeedbackTable from './FeedbackTable';

describe('containers/tables//Feedback/FeedbackTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllFeedbacks}>
        <FeedbackTable
          filter={{
            feedbackId: '',
            issueType: '',
            createdBy: '',
            createdAtRange: '',
          }}
          canViewDetails
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllFeedbacks}>
        <FeedbackTable
          filter={{
            feedbackId: '',
            issueType: '',
            createdBy: '',
            createdAtRange: '',
          }}
          canViewDetails
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
