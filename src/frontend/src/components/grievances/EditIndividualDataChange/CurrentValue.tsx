import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { LabelizedField } from '@core/LabelizedField';
import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { GrievanceFlexFieldPhotoModalNewIndividual } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalNewIndividual';
import { GrievanceIndividualPhotoModal } from '../GrievancesPhotoModals/GrievanceIndividualPhotoModal';
import type { ReactElement } from 'react';
import { ResponsiveGrid } from 'src/responsive';

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
  values;
}

export function CurrentValue({
  field,
  value,
  values,
}: CurrentValueProps): ReactElement {
  const location = useLocation();
  const isNewTicket = location.pathname.indexOf('new-ticket') !== -1;

  const { t } = useTranslation();
  let displayValue;
  switch (field?.type) {
    case 'SELECT_ONE':
      displayValue =
        field.choices?.find((item) => item.value === value)?.labelEn || '-';
      break;
    case 'SELECT_MANY':
      displayValue =
        field.choices?.find((item) => item.value === value)?.labelEn || '-';
      if (value instanceof Array) {
        displayValue = value
          .map(
            (choice) =>
              field.choices?.find((item) => item.value === choice)?.labelEn ||
              '-',
          )
          .join(', ');
      }
      break;
    case 'BOOL':
      displayValue = value === null ? '-' : value ? t('Yes') : t('No');
      break;
    case 'IMAGE':
      if (field?.name === 'photo' && !field?.isFlexField) {
        return (
          <ResponsiveGrid size="quarter">
            <GrievanceIndividualPhotoModal
              isCurrent
              individualId={values?.selectedIndividual?.id || null}
            />
          </ResponsiveGrid>
        );
      }
      return isNewTicket ? (
        <ResponsiveGrid size="quarter">
          <GrievanceFlexFieldPhotoModalNewIndividual
            flexField={field}
            individualId={values?.selectedIndividual?.id || null}
          />
        </ResponsiveGrid>
      ) : (
        <ResponsiveGrid size="quarter">
          <GrievanceFlexFieldPhotoModal isCurrent isIndividual field={field} />
        </ResponsiveGrid>
      );
    default:
      displayValue = value;
  }
  return (
    <ResponsiveGrid size="full">
      <LabelizedField label="Current Value" value={displayValue} />
    </ResponsiveGrid>
  );
}
