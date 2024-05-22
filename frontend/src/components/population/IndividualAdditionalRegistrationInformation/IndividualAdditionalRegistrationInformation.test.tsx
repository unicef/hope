import * as React from 'react';
import { fakeAllIndividualsFlexFieldsAttributes } from '../../../../fixtures/core/fakeAllIndividualsFlexFieldsAttributes';
import { fakeIndividual } from '../../../../fixtures/population/fakeIndividual';
import { render } from '../../../testUtils/testUtils';
import { IndividualAdditionalRegistrationInformation } from './IndividualAdditionalRegistrationInformation';

describe('components/population/IndividualAdditionalRegistrationInformation', () => {
  it('should render', () => {
    const { container } = render(
      <IndividualAdditionalRegistrationInformation
        individual={fakeIndividual}
        flexFieldsData={fakeAllIndividualsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
