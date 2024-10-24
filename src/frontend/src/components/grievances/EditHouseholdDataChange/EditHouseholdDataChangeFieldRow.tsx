import { Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field, useField } from 'formik';
import camelCase from 'lodash/camelCase';
import * as React from 'react';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import {
  AllEditHouseholdFieldsQuery,
  HouseholdQuery,
} from '@generated/graphql';
import { CurrentValue } from './CurrentValue';
import { EditHouseholdDataChangeField } from './EditHouseholdDataChangeField';

export interface EditHouseholdDataChangeFieldRowProps {
  fields: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'];
  household: HouseholdQuery['household'];
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => void;
  values;
}
export const EditHouseholdDataChangeFieldRow = ({
  fields,
  household,
  index,
  itemValue,
  notAvailableFields,
  onDelete,
  values,
}: EditHouseholdDataChangeFieldRowProps): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const field = fields.find((item) => item.name === itemValue.fieldName);
  const [, , helpers] = useField(
    `householdDataUpdateFields[${index}].isFlexField`,
  );
  const name = !field?.isFlexField
    ? camelCase(itemValue.fieldName)
    : itemValue.fieldName;
  useEffect(() => {
    helpers.setValue(field?.isFlexField);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemValue.fieldName]);
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={`householdDataUpdateFields[${index}].fieldName`}
          fullWidth
          variant="outlined"
          label={t('Field')}
          required
          component={FormikSelectField}
          choices={fields
            .filter(
              (item) =>
                !notAvailableFields.includes(item.name) ||
                item.name === itemValue?.fieldName,
            )
            .map((item) => ({
              value: item.name,
              name: item.labelEn,
            }))}
          disabled={isEditTicket}
        />
      </Grid>

      <CurrentValue
        field={field}
        value={
          !field?.isFlexField ? household[name] : household.flexFields[name]
        }
        values={values}
      />
      {itemValue.fieldName ? (
        <EditHouseholdDataChangeField
          name={`householdDataUpdateFields[${index}].fieldValue`}
          field={field}
        />
      ) : (
        <Grid item xs={4} />
      )}
      {itemValue.fieldName && (
        <Grid item xs={1}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      )}
    </>
  );
};
