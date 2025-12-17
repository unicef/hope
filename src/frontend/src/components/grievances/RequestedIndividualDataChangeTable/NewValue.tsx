import PhotoModal from '@core/PhotoModal/PhotoModal';
import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { GrievanceIndividualPhotoModal } from '../GrievancesPhotoModals/GrievanceIndividualPhotoModal';
import { ReactElement } from 'react';

export interface NewValueProps {
  field: {
    name?: string;
    type?: string;
    isFlexField?: boolean;
    choices?: Array<{
      value: any;
      labelEn?: string;
    }>;
  };
  value;
  fieldName?: string;
}

export function NewValue({ field, value, fieldName }: NewValueProps): ReactElement {
  // Handle core photo field - check both field.name and passed fieldName as fallback
  const isPhotoField = field?.name === 'photo' || (fieldName === 'photo' && !field?.isFlexField);

  if (isPhotoField && (field?.type === 'IMAGE' || !field)) {
    return <>{value ? <GrievanceIndividualPhotoModal photoPath={value} /> : '-'}</>;
  }

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
       
      displayValue = value === null ? '-' : value ? 'Yes' : 'No';
      break;
    case 'IMAGE':
      if (field?.isFlexField) {
        displayValue = (
          <GrievanceFlexFieldPhotoModal field={field} isIndividual />
        );
      } else if (field?.name === 'photo') {
        displayValue = <GrievanceIndividualPhotoModal photoPath={value} />;
      } else {
        displayValue = value ? <PhotoModal src={value} /> : '-';
      }
      break;
    default:
      displayValue = value;
  }
  return <>{displayValue || '-'}</>;
}
