import { fakeAllHouseholdsFlexFieldsAttributes } from '../../../../fixtures/core/fakeAllHouseholdsFlexFieldsAttributes';
import { fakeHousehold } from '../../../../fixtures/population/fakeHousehold';
import { render } from '../../../testUtils/testUtils';
import { HouseholdAdditionalRegistrationInformation } from './HouseholdAdditionalRegistrationInformation';

describe('components/population/HouseholdAdditionalRegistrationInformation', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdAdditionalRegistrationInformation
        household={fakeHousehold}
        flexFieldsData={fakeAllHouseholdsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
