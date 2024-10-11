import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { fakeDeliveryMechanisms } from '../../../../../fixtures/paymentmodule/fakeDeliveryMechanisms';
import { fakeFspsData } from '../../../../../fixtures/paymentmodule/fakeFspsData';
import { PERMISSIONS } from '../../../../config/permissions';
import { DeliveryMechanismRow } from './DeliveryMechanismRow';

describe('components/paymentmodule/CreateSetUpFsp/DeliveryMechanismRow', () => {
  it('should render', () => {
    const values = {
      deliveryMechanisms: [
        {
          deliveryMechanism: '',
          fsp: '',
          chosenConfiguration: '',
        },
      ],
    };
    const mapping = fakeFspsData?.availableFspsForDeliveryMechanisms[0];
    const mappedFsps = mapping?.fsps.map((el) => ({
      name: el.name,
      value: el.id,
    }));
    const deliveryMechanismsChoices =
      fakeDeliveryMechanisms.allDeliveryMechanisms.map((el) => ({
        name: el.name,
        value: el.value,
      }));

    const { container } = render(
      <DeliveryMechanismRow
        index={0}
        step={0}
        values={values}
        arrayHelpers={[]}
        deliveryMechanismsChoices={deliveryMechanismsChoices}
        fspsChoices={mappedFsps}
        permissions={[PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]}
        setFieldValue={() => {}}
      />,
    );

    expect(container).toMatchSnapshot();
  });
});
