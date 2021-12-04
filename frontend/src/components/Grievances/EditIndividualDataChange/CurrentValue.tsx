import { Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';
import { LabelizedField } from '../../LabelizedField';
import { GrievanceFlexFieldPhotoModal } from '../GrievanceFlexFieldPhotoModal';
import { GrievanceFlexFieldPhotoModalNewIndividual } from '../GrievanceFlexFieldPhotoModalNewIndividual';

export interface CurrentValueProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  value;
  values;
}

export function CurrentValue({
  field,
  value,
  values,
}: CurrentValueProps): React.ReactElement {
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
      /* eslint-disable-next-line no-nested-ternary */
      displayValue = value === null ? '-' : value ? t('Yes') : t('No');
      break;
    case 'IMAGE':
      return isNewTicket ? (
        <Grid item xs={3}>
          <GrievanceFlexFieldPhotoModalNewIndividual
            flexField={field}
            individualId={values?.selectedIndividual?.id || null}
          />
        </Grid>
      ) : (
        <Grid item xs={3}>
          <GrievanceFlexFieldPhotoModal isCurrent isIndividual field={field} />
        </Grid>
      );
    default:
      displayValue = value;
  }
  return (
    <Grid item xs={3}>
      <LabelizedField label='Current Value' value={displayValue} />
    </Grid>
  );
}
