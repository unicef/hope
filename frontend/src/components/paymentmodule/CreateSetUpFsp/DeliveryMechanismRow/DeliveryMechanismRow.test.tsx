import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { fakeDeliveryMechanisms } from '../../../../../fixtures/payments/fakeDeliveryMechanisms';
import { fakeFspsData } from '../../../../../fixtures/payments/fakeFspsData';
import { PERMISSIONS } from '../../../../config/permissions';
import { DeliveryMechanismRow } from './DeliveryMechanismRow';

describe('components/paymentmodule/CreateSetUpFsp/DeliveryMechanismRow', () => {
  it('should render', () => {
    const values = {
      deliveryMechanisms: [
        {
          deliveryMechanism: '',
          fsp: '',
        },
      ],
    };
    const mapping =
      fakeFspsData?.availableFspsForDeliveryMechanisms[0];
    const mappedFsps = mapping?.fsps.map((el) => ({
      name: el.name,
      value: el.id,
    }));
    const deliveryMechanismsChoices = fakeDeliveryMechanisms.allDeliveryMechanisms.map(
      (el) => ({
        name: el.name,
        value: el.value,
      }),
    );

    const { container } = render(
      <DeliveryMechanismRow
        index={0}
        step={0}
        values={values}
        arrayHelpers={[]}
        deliveryMechanismsChoices={deliveryMechanismsChoices}
        fspsChoices={mappedFsps}
        permissions={[PERMISSIONS.FINANCIAL_SERVICE_PROVIDER_REMOVE]}
      />,
    );

    expect(container).toMatchSnapshot();
  });
});
