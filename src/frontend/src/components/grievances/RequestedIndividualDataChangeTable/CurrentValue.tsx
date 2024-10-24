import * as React from 'react';
import { AllAddIndividualFieldsQuery } from '@generated/graphql';
import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';

export interface CurrentValueProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue;
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
      displayValue = (
        <GrievanceFlexFieldPhotoModal field={field} isCurrent isIndividual />
      );
      break;
    default:
      displayValue = value;
  }
  return <>{displayValue || '-'}</>;
}
