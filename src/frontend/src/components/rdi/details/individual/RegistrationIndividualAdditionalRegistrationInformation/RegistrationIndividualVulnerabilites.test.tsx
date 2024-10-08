import * as React from 'react';
import { RegistrationIndividualAdditionalRegistrationInformation } from '.';
import { fakeAllIndividualsFlexFieldsAttributes } from '../../../../../../fixtures/core/fakeAllIndividualsFlexFieldsAttributes';
import { fakeImportedIndividualDetailedFragment } from '../../../../../../fixtures/registration/fakeImportedIndividualDetailedFragment';
import { render } from '../../../../../testUtils/testUtils';

describe('components/rdi/details/individual/RegistrationIndividualAdditionalRegistrationInformation', () => {
  it('should render', () => {
    const { container } = render(
      <RegistrationIndividualAdditionalRegistrationInformation
        individual={fakeImportedIndividualDetailedFragment}
        flexFieldsData={fakeAllIndividualsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
