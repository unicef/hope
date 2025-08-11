import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { FieldArray } from 'formik';
import { useLocation } from 'react-router-dom';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { EditHouseholdDataChangeFieldRow } from './EditHouseholdDataChangeFieldRow';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdSmall } from '@restgenerated/models/HouseholdSmall';
import { HouseholdSimple } from '@restgenerated/models/HouseholdSimple';
import { HouseholdList } from '@restgenerated/models/HouseholdList';

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
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const isEditTicket = location.pathname.includes('edit-ticket');
  const household: HouseholdList = values.selectedHousehold;
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
      household.program.slug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id: household.id,
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

  const { data: householdFieldsData, isLoading: householdFieldsLoading } =
    useQuery({
      queryKey: ['householdFieldsAttributes', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList(
          {
            businessAreaSlug: businessArea,
          },
        ),
    });

  const householdFieldsDict = householdFieldsData;

  if (!household) {
    return (
      <div>{`You have to select a ${beneficiaryGroup?.groupLabel} earlier`}</div>
    );
  }
  if (fullHouseholdLoading || householdFieldsLoading || !fullHousehold) {
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
                    /* eslint-disable-next-line react/no-array-index-key */
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
      </>
    )
  );
}

export default withErrorBoundary(
  EditHouseholdDataChange,
  'EditHouseholdDataChange',
);
