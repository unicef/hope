import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

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
  const { businessArea } = useBaseUrl();

  const { data: areasData } = useQuery({
    queryKey: ['adminAreas', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGeoAreasList({
        businessAreaSlug: businessArea,
      }),
    enabled: field?.name === 'admin_area_title' && !!businessArea,
  });

  let displayValue;
  switch (field?.type) {
    case 'SELECT_ONE':
      if (field.name === 'admin_area_title') {
        const area = areasData?.find((a) => a.pCode === value);
        displayValue = area ? `${area.name} - ${area.pCode}` : value || '-';
      } else {
        displayValue =
          field.choices?.find((item) => item.value === value)?.labelEn ||
          value ||
          '-';
      }
      break;
    case 'SELECT_MANY':
      if (value instanceof Array) {
        displayValue = value
          .map(
            (choice) =>
              field.choices?.find((item) => item.value === choice)?.labelEn ||
              '-',
          )
          .join(', ');
      } else {
        displayValue =
          field.choices?.find((item) => item.value === value)?.labelEn || '-';
      }
      break;
    case 'BOOL':

      displayValue = value === null ? '-' : value ? 'Yes' : 'No';
      break;
    case 'IMAGE':
      displayValue = <GrievanceFlexFieldPhotoModal field={field} />;
      break;
    default:
      displayValue = value;
  }
  return <>{displayValue || '-'}</>;
}
