import { Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { LabelizedField } from '@core/LabelizedField';
import { GrievanceFlexFieldPhotoModal } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModal';
import { GrievanceFlexFieldPhotoModalNewIndividual } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalNewIndividual';
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
  let displayValue = value;
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
      displayValue = value === null ? '-' : value ? t('Yes') : t('No');
      break;
    case 'IMAGE':
      return isNewTicket ? (
        <Grid size={3}>
          <GrievanceFlexFieldPhotoModalNewIndividual
            flexField={field}
            individualId={values?.selectedIndividual?.id || null}
          />
        </Grid>
      ) : (
        <Grid size={3}>
          <GrievanceFlexFieldPhotoModal isCurrent isIndividual field={field} />
        </Grid>
      );
    default:
      displayValue = value;
  }
  return (
    <Grid size={3}>
      <LabelizedField label="Current Value" value={displayValue} />
    </Grid>
  );
}
