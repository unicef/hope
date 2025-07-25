import { Grid2 as Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { LabelizedField } from '@core/LabelizedField';
import { GrievanceFlexFieldPhotoModalNewHousehold } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalNewHousehold';
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
  const { t } = useTranslation();
  let displayValue;
  if (
    field?.name === 'country' ||
    field?.name === 'country_origin' ||
    field?.name === 'admin_area_title'
  ) {
    displayValue = value || '-';
  } else {
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
        return (
          <Grid size={{ xs: 3 }}>
            <GrievanceFlexFieldPhotoModalNewHousehold
              flexField={field}
              householdId={values?.selectedHousehold?.id || null}
            />
          </Grid>
        );
      default:
        displayValue = value;
    }
  }
  return (
    <Grid size={{ xs: 3 }}>
      <LabelizedField label={t('Current Value')} value={displayValue} />
    </Grid>
  );
}
