import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { ReactElement } from 'react';

export interface NewValueProps {
  field: {
    name?: string;
    type?: string;
    choices?: Array<{
      value: any;
      labelEn?: string;
    }>;
  };
  value;
}

export function NewValue({ field, value }: NewValueProps): ReactElement {
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
        <GrievanceFlexFieldPhotoModal field={field} isIndividual />
      );
      break;
    default:
      displayValue = value;
  }
  return <>{displayValue || '-'}</>;
}
