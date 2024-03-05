import * as React from 'react';
import { fakeAllHouseholdsFlexFieldsAttributes } from '../../../../fixtures/core/fakeAllHouseholdsFlexFieldsAttributes';
import { fakeHousehold } from '../../../../fixtures/population/fakeHousehold';
import { render } from '../../../testUtils/testUtils';
import { HouseholdVulnerabilities } from './HouseholdVulnerabilities';

describe('components/population/HouseholdVulnerabilities', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdVulnerabilities
        household={fakeHousehold}
        flexFieldsData={fakeAllHouseholdsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
