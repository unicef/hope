import React, { ReactElement, useEffect } from 'react';
import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { Field, FieldArray } from 'formik';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  AllHouseholdsQuery,
  useAllEditHouseholdFieldsQuery,
  useHouseholdChoiceDataQuery,
  useHouseholdLazyQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { EditHouseholdDataChangeFieldRow } from './EditHouseholdDataChangeFieldRow';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';

export interface EditHouseholdDataChangeProps {
  values;
  setFieldValue;
}

function EditHouseholdDataChange({
  values,
  setFieldValue,
}: EditHouseholdDataChangeProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const isEditTicket = location.pathname.includes('edit-ticket');
  const household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'] =
    values.selectedHousehold;
  const [getHousehold, { data: fullHousehold, loading: fullHouseholdLoading }] =
    useHouseholdLazyQuery({ variables: { id: household?.id } });

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

  useEffect(() => {
    if (
      fullHousehold?.household?.individualsAndRoles &&
      (!values.roles ||
        values.roles.length !==
          fullHousehold.household.individualsAndRoles.length)
    ) {
      console.log(
        'useefffect roles',
        fullHousehold.household.individualsAndRoles,
      );
      setFieldValue(
        'roles',
        fullHousehold.household.individualsAndRoles.map((roleItem) => ({
          individual: roleItem.individual.id,
          newRole: '',
        })),
      );
    }
  }, [fullHousehold, setFieldValue, values.roles]);

  const { data: householdFieldsData, loading: householdFieldsLoading } =
    useAllEditHouseholdFieldsQuery({ fetchPolicy: 'network-only' });
  const { data: choicesData, loading: householdsChoicesLoading } =
    useHouseholdChoiceDataQuery();
  const { roleChoices } = choicesData || {};
  const householdFieldsDict =
    householdFieldsData?.allEditHouseholdFieldsAttributes;

  if (!household) {
    return (
      <div>{`You have to select a ${beneficiaryGroup?.groupLabel} earlier`}</div>
    );
  }
  if (
    fullHouseholdLoading ||
    householdFieldsLoading ||
    !fullHousehold ||
    householdsChoicesLoading
  ) {
    return <LoadingComponent />;
  }
  const notAvailableItems = (values.householdDataUpdateFields || []).map(
    (fieldItem) => fieldItem.fieldName,
  );
  console.log('values.roles', values.roles);

  return (
    !isEditTicket && (
      <>
        <Title>
          <Typography variant="h6">{`${beneficiaryGroup?.groupLabel} Data`}</Typography>
        </Title>
        <Grid container spacing={3}>
          <FieldArray
            name="householdDataUpdateFields"
            render={(arrayHelpers) => (
              <>
                {(values.householdDataUpdateFields || []).map((item, index) => (
                  <EditHouseholdDataChangeFieldRow
                    key={`${index}-${item.fieldName}`}
                    itemValue={item}
                    index={index}
                    household={fullHousehold.household}
                    fields={householdFieldsDict}
                    notAvailableFields={notAvailableItems}
                    onDelete={() => arrayHelpers.remove(index)}
                    values={values}
                  />
                ))}
                <Grid size={{ xs: 4 }}>
                  <Button
                    color="primary"
                    startIcon={<AddCircleOutline />}
                    onClick={() => {
                      arrayHelpers.push({ fieldName: null, fieldValue: null });
                    }}
                    data-cy="button-add-new-field"
                  >
                    {t('Add new field')}
                  </Button>
                </Grid>
              </>
            )}
          />
        </Grid>

        {/* Roles in Household Section */}
        <Title>
          <Typography variant="h6">{t('Roles in Household')}</Typography>
        </Title>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 4 }}>
            <strong>{t('Full Name')}</strong>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <strong>{t('Current Role')}</strong>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <strong>{t('New Role')}</strong>
          </Grid>
          {fullHousehold.household.individualsAndRoles?.map(
            (roleItem, index) => (
              <React.Fragment key={roleItem.id}>
                <Grid size={{ xs: 4 }}>{roleItem.individual.fullName}</Grid>
                <Grid size={{ xs: 4 }}>{roleItem.role}</Grid>
                <Grid size={{ xs: 4 }}>
                  <Field
                    name={`roles.${index}.newRole`}
                    component={FormikSelectField}
                    label={t('New Role')}
                    choices={roleChoices}
                    fullWidth
                  />
                </Grid>
              </React.Fragment>
            ),
          )}
        </Grid>
      </>
    )
  );
}

export default withErrorBoundary(
  EditHouseholdDataChange,
  'EditHouseholdDataChange',
);
