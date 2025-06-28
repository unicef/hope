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
  const actualValue = value?.value;

  if (
    field?.name === 'country' ||
    field?.name === 'country_origin' ||
    field?.name === 'admin_area_title'
  ) {
    displayValue = actualValue || '-';
  } else {
    switch (field?.type) {
      case 'SELECT_ONE':
        displayValue =
          field.choices.find((item) => item.value === actualValue)?.labelEn ||
          '-';
        break;
      case 'SELECT_MANY':
        if (actualValue instanceof Array) {
          displayValue = actualValue
            .map(
              (choice) =>
                field.choices.find((item) => item.value === choice)?.labelEn ||
                '-',
            )
            .join(', ');
        } else {
          displayValue = '-';
        }
        break;
      case 'BOOL':
        /* eslint-disable-next-line no-nested-ternary */
        displayValue = actualValue === null ? '-' : actualValue ? 'Yes' : 'No';
        break;
      case 'IMAGE':
        displayValue = <GrievanceFlexFieldPhotoModal field={field} isCurrent />;
        break;
      default:
        displayValue =
          typeof actualValue === 'object'
            ? JSON.stringify(actualValue)
            : actualValue;
    }
  }
  return <>{displayValue || '-'}</>;
}
