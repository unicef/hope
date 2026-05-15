import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

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

  if (
    field?.name === 'country' ||
    field?.name === 'country_origin' ||
    field?.name === 'admin_area_title'
  ) {
    if (field.name === 'admin_area_title') {
      const area = areasData?.find((a) => a.pCode === value);
      displayValue = area ? `${area.name} - ${area.pCode}` : value || '-';
    } else {
      displayValue = value || '-';
    }
  } else {
    switch (field?.type) {
      case 'SELECT_ONE':
        displayValue =
          field.choices?.find((item) => item.value === value)?.labelEn || '-';
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
          displayValue = '-';
        }
        break;
      case 'BOOL':

        displayValue = value === null ? '-' : value ? 'Yes' : 'No';
        break;
      case 'IMAGE':
        displayValue = <GrievanceFlexFieldPhotoModal field={field} isCurrent />;
        break;
      default:
        displayValue =
          typeof value === 'object' && value !== null && 'value' in value
            ? value.value
            : value;
    }
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
