import { Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { Field, useField } from 'formik';
import camelCase from 'lodash/camelCase';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import {
  AllEditHouseholdFieldsQuery,
  HouseholdQuery,
} from '../../../__generated__/graphql';
import { CurrentValue } from './CurrentValue';
import { EditHouseholdDataChangeField } from './EditHouseholdDataChangeField';

export interface EditHouseholdDataChangeFieldRowProps {
  fields: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'];
  household: HouseholdQuery['household'];
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => {};
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
          variant='outlined'
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
          <IconButton onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      )}
    </>
  );
};
