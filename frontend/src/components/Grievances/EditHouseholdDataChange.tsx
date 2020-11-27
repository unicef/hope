import React, { useEffect } from 'react';
import { Button, Grid, IconButton, Typography } from '@material-ui/core';
import styled from 'styled-components';
import { Field, FieldArray } from 'formik';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { AddCircleOutline, Delete } from '@material-ui/icons';
import camelCase from 'lodash/camelCase';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import {
  AllEditHouseholdFieldsQuery,
  AllHouseholdsQuery,
  HouseholdQuery,
  useAllEditHouseholdFieldsQuery,
  useHouseholdQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { LabelizedField } from '../LabelizedField';

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;

export interface EditHouseholdDataChangeField {
  field: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  name: string;
}
export const EditHouseholdDataChangeField = ({
  name,
  field,
}: EditHouseholdDataChangeField): React.ReactElement => {
  let fieldProps;
  switch (field.type) {
    case 'STRING':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'INTEGER':
      fieldProps = {
        component: FormikTextField,
        type: 'number',
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        decoratorEnd: <CalendarTodayRoundedIcon color='disabled' />,
      };
      break;

    case 'BOOL':
      fieldProps = {
        component: FormikCheckboxField,
      };
      break;
    default:
      fieldProps = {};
  }
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={name}
          fullWidth
          variant='outlined'
          label={field.labelEn}
          required={field.required}
          {...fieldProps}
        />
      </Grid>
    </>
  );
};

export interface CurrentValueProps {
  field: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue;
  if (field?.name === 'country' || field?.name === 'country_origin') {
    displayValue = value || '-';
  } else {
    switch (field?.type) {
      case 'SELECT_ONE':
        displayValue =
          field.choices.find((item) => item.value === value)?.labelEn || '-';
        break;
      case 'BOOL':
        /* eslint-disable-next-line no-nested-ternary */
        displayValue = value === null ? '-' : value ? 'Yes' : 'No';
        break;
      default:
        displayValue = value;
    }
  }
  return (
    <Grid item xs={3}>
      <LabelizedField label='Current Value' value={displayValue || '-'} />
    </Grid>
  );
}

export interface EditHouseholdDataChangeFieldRowProps {
  fields: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'];
  household: HouseholdQuery['household'];
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => {};
}
export const EditHouseholdDataChangeFieldRow = ({
  fields,
  household,
  index,
  itemValue,
  notAvailableFields,
  onDelete,
}: EditHouseholdDataChangeFieldRowProps): React.ReactElement => {
  const field = fields.find((item) => item.name === itemValue.fieldName);
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={`householdDataUpdateFields[${index}].fieldName`}
          fullWidth
          variant='outlined'
          label='Field'
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
        value={household[camelCase(itemValue.fieldName)]}
      />
      {itemValue.fieldName ? (
        <EditHouseholdDataChangeField
          name={`householdDataUpdateFields[${index}].fieldValue`}
          field={field}
        />
      ) : (
        <Grid item xs={4} />
      )}
      <Grid item xs={1}>
        <IconButton onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>
    </>
  );
};
export interface EditHouseholdDataChangeProps {
  household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'];
  values;
  setFieldValue;
}
export const EditHouseholdDataChange = ({
  household,
  values,
  setFieldValue,
}: EditHouseholdDataChangeProps): React.ReactElement => {
  const {
    data: fullHousehold,
    loading: fullHouseholdLoading,
  } = useHouseholdQuery({ variables: { id: household?.id } });
  useEffect(() => {
    setFieldValue('householdDataUpdateFields', [
      { fieldName: null, fieldValue: null },
    ]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const {
    data: householdFieldsData,
    loading: householdFieldsLoading,
  } = useAllEditHouseholdFieldsQuery();
  if (fullHouseholdLoading || householdFieldsLoading) {
    return <LoadingComponent />;
  }
  if (!household) {
    return <div>You have to select a household earlier</div>;
  }
  const notAvailableItems = (values.householdDataUpdateFields || []).map(
    (fieldItem) => fieldItem.fieldName,
  );
  return (
    <>
      <Title>
        <Typography variant='h6'>Household Data</Typography>
      </Title>
      <Grid container spacing={3}>
        <FieldArray
          name='householdDataUpdateFields'
          render={(arrayHelpers) => (
            <>
              {(values.householdDataUpdateFields || []).map((item, index) => (
                <EditHouseholdDataChangeFieldRow
                  itemValue={item}
                  index={index}
                  household={fullHousehold.household}
                  fields={householdFieldsData.allEditHouseholdFieldsAttributes}
                  notAvailableFields={notAvailableItems}
                  onDelete={() => arrayHelpers.remove(index)}
                />
              ))}
              <Grid item xs={4}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({ fieldName: null, fieldValue: null });
                  }}
                >
                  <AddIcon />
                  Add new field
                </Button>
              </Grid>
            </>
          )}
        />
      </Grid>
    </>
  );
};
