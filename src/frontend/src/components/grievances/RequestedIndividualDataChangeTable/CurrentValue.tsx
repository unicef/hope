import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { ReactElement } from 'react';

export interface CurrentValueProps {
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

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): ReactElement {
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
      displayValue =
        typeof value === 'object' && value !== null && 'value' in value
          ? value.value
          : value;
  }
  return (
    <>
      {displayValue === null ||
      displayValue === 'null' ||
      displayValue === undefined ||
      displayValue === ''
        ? '-'
        : displayValue}
    </>
  );
}
