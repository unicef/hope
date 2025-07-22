import React, { ReactElement, useEffect } from 'react';
import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { Field, FieldArray } from 'formik';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { AddCircleOutline, Delete } from '@mui/icons-material';
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
import { DarkGrey } from '@components/grievances/LookUps/LookUpStyles';

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
      (!values.roles || values.roles.length === 0)
    ) {
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
          <Grid size={{ xs: 3 }}>
            <strong>{t('New Role')}</strong>
          </Grid>
          <Grid size={{ xs: 1 }}></Grid>
          {/* Render all roles, including added ones */}
          {(values.roles || []).map((roleItem, index) => {
            const currentRoleObj =
              fullHousehold.household.individualsAndRoles.find(
                (r) => r.individual.id === roleItem.individual,
              );
            // Filter out individuals already assigned in other rows
            const usedIds = (values.roles || []).map((r, i) =>
              i !== index ? r.individual : null,
            );
            const availableChoices = fullHousehold.household.individuals.edges
              .map((ind) => ({ value: ind.node.id, label: ind.node.fullName }))
              .filter((choice) => !usedIds.includes(choice.value));
            return (
              <React.Fragment key={roleItem.individual + '-' + index}>
                <Grid size={{ xs: 4 }}>
                  <Field
                    name={`roles.${index}.individual`}
                    component={FormikSelectField}
                    label={t('Individual')}
                    choices={availableChoices}
                    fullWidth
                  />
                </Grid>
                <Grid size={{ xs: 4 }}>
                  {currentRoleObj ? currentRoleObj.role : 'None'}
                </Grid>
                <Grid size={{ xs: 3 }}>
                  <Field
                    name={`roles.${index}.newRole`}
                    component={FormikSelectField}
                    label={t('New Role')}
                    choices={roleChoices}
                    fullWidth
                  />
                </Grid>
                <Grid size={{ xs: 1 }}>
                  <Button
                    color="secondary"
                    onClick={() => {
                      const updatedRoles = [...(values.roles || [])];
                      updatedRoles.splice(index, 1);
                      setFieldValue('roles', updatedRoles);
                    }}
                    data-cy={`button-remove-role-${index}`}
                  >
                    <DarkGrey>
                      <Delete />
                    </DarkGrey>
                  </Button>
                </Grid>
              </React.Fragment>
            );
          })}
          {/* Add a New Role button */}
          <Grid size={{ xs: 12 }} style={{ marginTop: 16 }}>
            <Button
              color="primary"
              startIcon={<AddCircleOutline />}
              onClick={() => {
                // Find individuals not already assigned in roles
                const usedIds = (values.roles || []).map((r) => r.individual);
                const availableIndividuals =
                  fullHousehold.household.individuals.edges
                    .map((edge) => edge.node)
                    .filter((ind) => !usedIds.includes(ind.id));
                const defaultIndividual =
                  availableIndividuals.length > 0
                    ? availableIndividuals[0].id
                    : '';
                setFieldValue('roles', [
                  ...(values.roles || []),
                  {
                    individual: defaultIndividual,
                    newRole: '',
                  },
                ]);
              }}
              data-cy="button-add-new-role"
            >
              {t('Add a New Role')}
            </Button>
          </Grid>
        </Grid>
      </>
    )
  );
}

export default withErrorBoundary(
  EditHouseholdDataChange,
  'EditHouseholdDataChange',
);
