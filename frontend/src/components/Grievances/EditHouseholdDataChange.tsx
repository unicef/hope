import { Button, Grid, IconButton, Typography } from '@material-ui/core';
import { useLocation } from 'react-router-dom';
import { AddCircleOutline, Delete } from '@material-ui/icons';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, FieldArray, useField } from 'formik';
import camelCase from 'lodash/camelCase';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikDecimalField } from '../../shared/Formik/FormikDecimalField';
import { FormikFileField } from '../../shared/Formik/FormikFileField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import {
  AllEditHouseholdFieldsQuery,
  AllHouseholdsQuery,
  HouseholdQuery,
  useAllEditHouseholdFieldsQuery,
  useHouseholdLazyQuery,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { LoadingComponent } from '../LoadingComponent';
import { FormikBoolFieldGrievances } from './FormikBoolFieldGrievances';
import { GrievanceFlexFieldPhotoModalEditable } from './GrievanceFlexFieldPhotoModalEditable';
import { GrievanceFlexFieldPhotoModalNewHousehold } from './GrievanceFlexFieldPhotoModalNewHousehold';

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
  const location = useLocation();
  const isNewTicket = location.pathname.indexOf('new-ticket') !== -1;

  let fieldProps;
  switch (field.type) {
    case 'DECIMAL':
      fieldProps = {
        component: FormikDecimalField,
      };
      break;
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
        component: FormikBoolFieldGrievances,
        required: field.required,
      };
      break;
    case 'IMAGE':
      fieldProps = {
        component: isNewTicket
          ? FormikFileField
          : GrievanceFlexFieldPhotoModalEditable,
        flexField: field,
        isIndividual: false,
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
  values;
}

export function CurrentValue({
  field,
  value,
  values,
}: CurrentValueProps): React.ReactElement {
  const { t } = useTranslation();
  let displayValue;
  if (field?.name === 'country' || field?.name === 'country_origin' || field?.name === "admin_area_title") {
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
          <Grid item xs={3}>
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
    <Grid item xs={3}>
      <LabelizedField label={t('Current Value')} value={displayValue} />
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
      <Grid item xs={1}>
        <IconButton onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>
    </>
  );
};
export interface EditHouseholdDataChangeProps {
  values;
  setFieldValue;
}
export const EditHouseholdDataChange = ({
  values,
  setFieldValue,
}: EditHouseholdDataChangeProps): React.ReactElement => {
  const { t } = useTranslation();
  const household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'] =
    values.selectedHousehold;
  const [
    getHousehold,
    { data: fullHousehold, loading: fullHouseholdLoading },
  ] = useHouseholdLazyQuery({ variables: { id: household?.id } });
  useEffect(() => {
    if (values.selectedHousehold) {
      getHousehold();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [values.selectedHousehold]);
  useEffect(() => {
    if (
      !values.householdDataUpdateFields ||
      values.householdDataUpdateFields.length === 0
    ) {
      setFieldValue('householdDataUpdateFields', [
        { fieldName: null, fieldValue: '' },
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const {
    data: householdFieldsData,
    loading: householdFieldsLoading,
  } = useAllEditHouseholdFieldsQuery();
  if (!household) {
    return <div>{t('You have to select a household earlier')}</div>;
  }
  if (fullHouseholdLoading || householdFieldsLoading || !fullHousehold) {
    return <LoadingComponent />;
  }
  const notAvailableItems = (values.householdDataUpdateFields || []).map(
    (fieldItem) => fieldItem.fieldName,
  );
  return (
    <>
      <Title>
        <Typography variant='h6'>{t('Household Data')}</Typography>
      </Title>
      <Grid container spacing={3}>
        <FieldArray
          name='householdDataUpdateFields'
          render={(arrayHelpers) => (
            <>
              {(values.householdDataUpdateFields || []).map((item, index) => (
                <EditHouseholdDataChangeFieldRow
                  /* eslint-disable-next-line react/no-array-index-key */
                  key={`${index}-${item.fieldName}`}
                  itemValue={item}
                  index={index}
                  household={fullHousehold.household}
                  fields={householdFieldsData.allEditHouseholdFieldsAttributes}
                  notAvailableFields={notAvailableItems}
                  onDelete={() => arrayHelpers.remove(index)}
                  values={values}
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
                  {t('Add new field')}
                </Button>
              </Grid>
            </>
          )}
        />
      </Grid>
    </>
  );
};
