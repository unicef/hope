import React from 'react';
import { AllEditHouseholdFieldsQuery } from '../../../__generated__/graphql';
import { GrievanceFlexFieldPhotoModal } from '../GrievanceFlexFieldPhotoModal';

export interface CurrentValueProps {
  field: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue;
  if (
    field?.name === 'country' ||
    field?.name === 'country_origin' ||
    field?.name === 'admin_area_title'
  ) {
    displayValue = value || '-';
  } else {
    switch (field?.type) {
      case 'SELECT_ONE':
        displayValue =
          field.choices.find((item) => item.value === value)?.labelEn || '-';
        break;
      case 'SELECT_MANY':
        displayValue =
          field.choices.find((item) => item.value === value)?.labelEn || '-';
        if (value instanceof Array) {
          displayValue = value
            .map(
              (choice) =>
                field.choices.find((item) => item.value === choice)?.labelEn ||
                '-',
            )
            .join(', ');
        }
        break;
      case 'BOOL':
        /* eslint-disable-next-line no-nested-ternary */
        displayValue = value === null ? '-' : value ? 'Yes' : 'No';
        break;
      case 'IMAGE':
        displayValue = <GrievanceFlexFieldPhotoModal field={field} isCurrent />;
        break;
      default:
        displayValue = value;
    }
  }
  return <>{displayValue || '-'}</>;
}
