import PhotoModal from '@core/PhotoModal/PhotoModal';
import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { GrievanceIndividualPhotoModal } from '../GrievancesPhotoModals/GrievanceIndividualPhotoModal';
import { ReactElement } from 'react';

export interface CurrentValueProps {
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
  individualId?: string;
  fieldName?: string;
}

export function CurrentValue({
  field,
  value,
  individualId,
  fieldName,
}: CurrentValueProps): ReactElement {
  // Handle core photo field - check both field.name and passed fieldName as fallback
  const isPhotoField = field?.name === 'photo' || (fieldName === 'photo' && !field?.isFlexField);

  if (isPhotoField && (field?.type === 'IMAGE' || !field)) {
    return <>{individualId ? <GrievanceIndividualPhotoModal isCurrent individualId={individualId} /> : '-'}</>;
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
          <GrievanceFlexFieldPhotoModal field={field} isCurrent isIndividual />
        );
      } else if (field?.name === 'photo') {
        displayValue = (
          <GrievanceIndividualPhotoModal isCurrent individualId={individualId} />
        );
      } else {
        displayValue = value ? <PhotoModal src={value} /> : '-';
      }
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
