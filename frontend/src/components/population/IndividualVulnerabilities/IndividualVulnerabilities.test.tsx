import * as React from 'react';
import { fakeAllIndividualsFlexFieldsAttributes } from '../../../../fixtures/core/fakeAllIndividualsFlexFieldsAttributes';
import { fakeIndividual } from '../../../../fixtures/population/fakeIndividual';
import { render } from '../../../testUtils/testUtils';
import { IndividualVulnerabilities } from './IndividualVunerabilities';

describe('components/population/IndividualVulnerabilities', () => {
  it('should render', () => {
    const { container } = render(
      <IndividualVulnerabilities
        individual={fakeIndividual}
        flexFieldsData={fakeAllIndividualsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
