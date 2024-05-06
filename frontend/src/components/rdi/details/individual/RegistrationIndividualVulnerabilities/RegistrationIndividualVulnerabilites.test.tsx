import * as React from 'react';
import { RegistrationIndividualVulnerabilities } from '.';
import { fakeAllIndividualsFlexFieldsAttributes } from '../../../../../../fixtures/core/fakeAllIndividualsFlexFieldsAttributes';
import { fakeImportedIndividualDetailedFragment } from '../../../../../../fixtures/registration/fakeImportedIndividualDetailedFragment';
import { render } from '../../../../../testUtils/testUtils';

describe('components/rdi/details/individual/RegistrationIndividualVulnerabilities', () => {
  it('should render', () => {
    const { container } = render(
      <RegistrationIndividualVulnerabilities
        individual={fakeImportedIndividualDetailedFragment}
        flexFieldsData={fakeAllIndividualsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
