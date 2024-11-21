import {
  AllEditHouseholdFieldsQuery,
  AllEditPeopleFieldsQuery,
} from '@generated/graphql';
import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { ReactElement } from 'react';

export interface CurrentValueProps {
  field:
    | AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number]
    | AllEditPeopleFieldsQuery['allEditPeopleFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): ReactElement {
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
