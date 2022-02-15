import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { GrievancesApproveSection } from './GrievancesApproveSection';
import { fakeGrievanceTicket } from '../../../../fixtures/grievances/fakeGrievanceTicket';

describe('components/grievances/GrievancesApproveSection', () => {
  it('should render', () => {
    const { container } = render(
      <GrievancesApproveSection
        businessArea='afghanistan'
        ticket={fakeGrievanceTicket}
        canApproveFlagAndAdjudication={true}
        canApproveDataChange={true}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
