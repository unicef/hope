import React, { ReactElement, useEffect } from 'react';
import { Button, Grid, Typography } from '@mui/material';
import { Field, FieldArray } from 'formik';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { AddCircleOutline, Delete } from '@mui/icons-material';
import Tooltip from '@mui/material/Tooltip';
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
  programSlug?: string;
}

function EditHouseholdDataChange({
  values,
  setFieldValue,
  programSlug,
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
      programSlug,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id: household.id,
        programSlug: programSlug,
      }),
    enabled: Boolean(household && businessArea && programSlug),
  });

  // Fetch household members for roles logic
  const { data: householdMembers, isLoading: membersLoading } = useQuery({
    queryKey: [
      'householdMembers',
      businessArea,
      household.id,
      programSlug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsMembersList({
        businessAreaSlug: businessArea,
        id: household.id,
        programSlug: programSlug,
      }),
    enabled: Boolean(household && businessArea && programSlug),
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
      const membersWithRole = householdMembers.results.filter(
        (member) => member.role && member.role !== null,
      );
      setFieldValue(
        'roles',
        membersWithRole.map((member) => ({
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

                <Grid size={4}>
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
          <Grid size={4}>
            <strong>{t('Full Name')}</strong>
          </Grid>
          <Grid size={4}>
            <strong>{t('Current Role')}</strong>
          </Grid>
          <Grid size={3}>
            <strong>{t('New Role')}</strong>
          </Grid>
          <Grid size={1}></Grid>
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
            // Only show trash can for roles added via 'Add a New Role' button (i.e., those with empty currentRoleObj)
            const isNewRole = !currentRoleObj;
            return (
              <React.Fragment key={roleItem.individual + '-' + index}>
                <Grid size={4}>
                  <Field
                    name={`roles.${index}.individual`}
                    component={FormikSelectField}
                    label={t('Individual')}
                    choices={availableChoices}
                    fullWidth
                  />
                </Grid>
                <Grid size={4}>
                  {currentRoleObj
                    ? roleDisplayMap[currentRoleObj.role] || currentRoleObj.role
                    : 'None'}
                </Grid>
                <Grid size={3}>
                  <Field
                    name={`roles.${index}.newRole`}
                    component={FormikSelectField}
                    label={t('New Role')}
                    choices={roleChoices}
                    fullWidth
                  />
                </Grid>
                <Grid size={1}>
                  {isNewRole && (
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
                  )}
                </Grid>
              </React.Fragment>
            );
          })}
          {/* Add a New Role button */}
          <Grid size={12} sx={{ marginTop: 12 }}>
            {(() => {
              const usedIds = (values.roles || []).map((r) => r.individual);
              const availableIndividuals = householdMembers.results.filter(
                (ind) => !usedIds.includes(ind.id),
              );
              const isDisabled = availableIndividuals.length === 0;
              return (
                <Tooltip
                  title={isDisabled ? t('No more roles available') : ''}
                  placement="top"
                  arrow
                  disableHoverListener={!isDisabled}
                >
                  <span>
                    <Button
                      color="primary"
                      startIcon={<AddCircleOutline />}
                      onClick={() => {
                        if (availableIndividuals.length > 0) {
                          const defaultIndividual = availableIndividuals[0].id;
                          // Find current role for this individual
                          const currentRoleObj =
                            fullHousehold.rolesInHousehold.find(
                              (r) => r.individual.id === defaultIndividual,
                            );
                          // Only add if newRole is not equal to current role
                          if (!currentRoleObj || '' !== currentRoleObj.role) {
                            setFieldValue('roles', [
                              ...(values.roles || []),
                              {
                                individual: defaultIndividual,
                                newRole: '',
                              },
                            ]);
                          }
                        }
                      }}
                      data-cy="button-add-new-role"
                      disabled={isDisabled}
                    >
                      {t('Add a New Role')}
                    </Button>
                  </span>
                </Tooltip>
              );
            })()}
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
