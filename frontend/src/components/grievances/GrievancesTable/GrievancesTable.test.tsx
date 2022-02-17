import React from 'react';
import { MockedProvider } from '@apollo/client/testing';
import { render } from '../../../testUtils/testUtils';
import { GrievancesTable } from './GrievancesTable';

describe('components/grievances/GrievancesTable', () => {
  it('should render', () => {
    const mockedFilter = {
      search: '',
      status: '',
      fsp: '',
      createdAtRange: '',
      admin: null,
      registrationDataImport: null,
      cashPlanPaymentVerification: null,
    };
    const { container } = render(
      <MockedProvider mocks={[]}>
        <GrievancesTable businessArea='afghanistan' filter={mockedFilter} />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
  });
});
