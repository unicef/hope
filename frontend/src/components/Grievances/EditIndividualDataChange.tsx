import { Box, Button, Grid, IconButton, Typography } from '@material-ui/core';
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
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
  IndividualQuery,
  useAllAddIndividualFieldsQuery,
  useIndividualLazyQuery,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { LoadingComponent } from '../LoadingComponent';
import { PhotoPreview } from '../PhotoPreview';
import { ExistingDocumentFieldArray } from './ExistingDocumentFieldArray';
import { ExistingIdentityFieldArray } from './ExistingIdentityFieldArray';
import { FormikBoolFieldGrievances } from './FormikBoolFieldGrievances';
import { NewDocumentFieldArray } from './NewDocumentFieldArray';
import { NewIdentityFieldArray } from './NewIdentityFieldArray';

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;

const Image = styled.img`
  max-width: 150px;
`;

export interface EditIndividualDataChangeField {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  name: string;
}
export const EditIndividualDataChangeField = ({
  name,
  field,
}: EditIndividualDataChangeField): React.ReactElement => {
  let fieldProps;
  switch (field.type) {
    case 'DECIMAL':
      fieldProps = {
        fullWidth: true,
        component: FormikDecimalField,
      };
      break;
    case 'INTEGER':
      fieldProps = {
        component: FormikTextField,
        type: 'number',
      };
      break;
    case 'STRING':
      fieldProps = {
        fullWidth: true,
        component: FormikTextField,
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        fullWidth: true,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        fullWidth: true,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        fullWidth: true,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        fullWidth: true,
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
        component: FormikFileField,
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
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
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
      return (
        <Grid item xs={3}>
          <PhotoPreview src={value}>
            <Image src={value} />
          </PhotoPreview>
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

export interface EditIndividualDataChangeFieldRowProps {
  fields: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'];
  individual: IndividualQuery['individual'];
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => {};
}
export const EditIndividualDataChangeFieldRow = ({
  fields,
  individual,
  index,
  itemValue,
  notAvailableFields,
  onDelete,
}: EditIndividualDataChangeFieldRowProps): React.ReactElement => {
  const field = fields.find((item) => item.name === itemValue.fieldName);
  // eslint-disable-next-line
  const [fieldNotUsed, metaNotUsed, helpers] = useField(
    `individualDataUpdateFields[${index}].isFlexField`,
  );
  useEffect(() => {
    helpers.setValue(field?.isFlexField);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemValue.fieldName]);

  return (
    <>
      <Grid item xs={4}>
        <Field
          name={`individualDataUpdateFields[${index}].fieldName`}
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
        value={
          !field?.isFlexField
            ? individual[camelCase(itemValue.fieldName)]
            : individual.flexFields[itemValue.fieldName]
        }
      />
      {itemValue.fieldName ? (
        <EditIndividualDataChangeField
          name={`individualDataUpdateFields[${index}].fieldValue`}
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

export interface EditIndividualDataChangeProps {
  values;
  setFieldValue;
}

export const EditIndividualDataChange = ({
  values,
  setFieldValue,
}: EditIndividualDataChangeProps): React.ReactElement => {
  const { t } = useTranslation();
  const individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'] =
    values.selectedIndividual;
  const {
    data: addIndividualFieldsData,
    loading: addIndividualFieldsLoading,
  } = useAllAddIndividualFieldsQuery();

  const [
    getIndividual,
    { data: fullIndividual, loading: fullIndividualLoading },
  ] = useIndividualLazyQuery({ variables: { id: individual?.id } });

  useEffect(() => {
    if (individual) {
      getIndividual();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [values.selectedIndividual]);

  useEffect(() => {
    if (
      !values.individualDataUpdateFields ||
      values.individualDataUpdateFields.length === 0
    ) {
      setFieldValue('individualDataUpdateFields', [
        { fieldName: null, fieldValue: null },
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const { data, loading } = useAllAddIndividualFieldsQuery();
  if (!individual) {
    return <div>{t('You have to select an individual earlier')}</div>;
  }
  if (
    loading ||
    fullIndividualLoading ||
    addIndividualFieldsLoading ||
    !fullIndividual
  ) {
    return <LoadingComponent />;
  }
  const notAvailableItems = (values.individualDataUpdateFields || []).map(
    (fieldItem) => fieldItem.fieldName,
  );
  return (
    <>
      <BoxWithBorders>
        <Title>
          <Typography variant='h6'>{t('Bio Data')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <FieldArray
            name='individualDataUpdateFields'
            render={(arrayHelpers) => (
              <>
                {(values.individualDataUpdateFields || []).map(
                  (item, index) => (
                    <EditIndividualDataChangeFieldRow
                      // eslint-disable-next-line react/no-array-index-key
                      key={`${index}-${item?.fieldName}`}
                      itemValue={item}
                      index={index}
                      individual={fullIndividual.individual}
                      fields={data.allAddIndividualsFieldsAttributes}
                      notAvailableFields={notAvailableItems}
                      onDelete={() => arrayHelpers.remove(index)}
                    />
                  ),
                )}
                <Grid item xs={4}>
                  <Button
                    color='primary'
                    onClick={() => {
                      arrayHelpers.push({ fieldName: null, fieldValue: '' });
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
      </BoxWithBorders>
      <Box mt={3}>
        <Title>
          <Typography variant='h6'>{t('Documents')}</Typography>
        </Title>
        <ExistingDocumentFieldArray
          values={values}
          setFieldValue={setFieldValue}
          individual={individual}
        />
        <NewDocumentFieldArray
          values={values}
          addIndividualFieldsData={addIndividualFieldsData}
        />
      </Box>
      <Box mt={3}>
        <Title>
          <Typography variant='h6'>{t('Identities')}</Typography>
        </Title>
        <ExistingIdentityFieldArray
          values={values}
          setFieldValue={setFieldValue}
          individual={individual}
        />
        <NewIdentityFieldArray
          values={values}
          addIndividualFieldsData={addIndividualFieldsData}
        />
      </Box>
    </>
  );
};
