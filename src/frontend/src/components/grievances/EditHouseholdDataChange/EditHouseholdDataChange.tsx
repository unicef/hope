import React, { ReactElement, useEffect } from 'react';
import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { Field, FieldArray } from 'formik';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { AddCircleOutline, Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { EditHouseholdDataChangeFieldRow } from './EditHouseholdDataChangeFieldRow';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { DarkGrey } from '@components/grievances/LookUps/LookUpStyles';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { useQuery } from '@tanstack/react-query';
import { roleDisplayMap } from '@components/grievances/utils/createGrievanceUtils';

export interface EditHouseholdDataChangeProps {
  values;
  setFieldValue;
}

function EditHouseholdDataChange({
  values,
  setFieldValue,
}: EditHouseholdDataChangeProps): ReactElement {
  const { businessArea, programId } = useBaseUrl();

  const { data: individualsChoices } = useQuery({
    queryKey: ['individualsChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasIndividualsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
    enabled: Boolean(businessArea),
  });
  const roleChoices = individualsChoices?.roleChoices || [];
  const { t } = useTranslation();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const isEditTicket = location.pathname.includes('edit-ticket');
  const household: HouseholdDetail = values.selectedHousehold;

  const { data: householdFieldsData, isLoading: householdFieldsLoading } =
    useQuery({
      queryKey: ['householdFields', businessArea, programId],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList(
          {
            businessAreaSlug: businessArea,
          },
        ),
      enabled: Boolean(businessArea),
    });

  const {
    data: fullHousehold,
    isLoading: fullHouseholdLoading,
    refetch: refetchHousehold,
  } = useQuery<HouseholdDetail>({
    queryKey: [
      'household',
      businessArea,
      household.id,
      programId,
      //@ts-ignore
      household.program.slug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id: household.id,
        //@ts-ignore
        programSlug: household.program.slug,
        // Define roleChoices for New Role select field
      }),
    enabled: Boolean(household && businessArea),
  });

  // Fetch household members for roles logic
  const { data: householdMembers, isLoading: membersLoading } = useQuery({
    queryKey: [
      'householdMembers',
      businessArea,
      household.id,
      //@ts-ignore
      household.program.slug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsMembersList({
        businessAreaSlug: businessArea,
        id: household.id,
        //@ts-ignore
        programSlug: household.program.slug,
      }),
    enabled: Boolean(household && businessArea),
  });

  useEffect(() => {
    if (values.selectedHousehold) {
      refetchHousehold();
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
    if (householdMembers && (!values.roles || values.roles.length === 0)) {
      setFieldValue(
        'roles',
        householdMembers.results.map((member) => ({
          individual: member.id,
          newRole: '',
        })),
      );
    }
  }, [householdMembers, setFieldValue, values.roles]);

  const householdFieldsDict = householdFieldsData;

  if (!household) {
    return (
      <div>{`You have to select a ${beneficiaryGroup?.groupLabel} earlier`}</div>
    );
  }
  if (
    fullHouseholdLoading ||
    householdFieldsLoading ||
    !fullHousehold ||
    membersLoading ||
    !householdMembers
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
                    household={fullHousehold}
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
            // Find individual details from householdMembers
            const currentRoleObj = fullHousehold.rolesInHousehold.find(
              (r) => r.individual.id === roleItem.individual,
            );

            // Filter out individuals already assigned in other rows
            const usedIds = (values.roles || []).map((r, i) =>
              i !== index ? r.individual : null,
            );
            const availableChoices = householdMembers.results
              .map((ind) => ({ value: ind.id, label: ind.fullName }))
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
                  {currentRoleObj
                    ? roleDisplayMap[currentRoleObj.role] || currentRoleObj.role
                    : 'None'}
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
                const availableIndividuals = householdMembers.results.filter(
                  (ind) => !usedIds.includes(ind.id),
                );
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
