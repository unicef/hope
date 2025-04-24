import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { FieldArray } from 'formik';
import { useLocation } from 'react-router-dom';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllHouseholdsQuery,
  useAllEditHouseholdFieldsQuery,
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
  const { data: householdFieldsData, loading: householdFieldsLoading } =
    useAllEditHouseholdFieldsQuery();

  const householdFieldsDict =
    householdFieldsData?.allEditHouseholdFieldsAttributes;

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
      </>
    )
  );
}

export default withErrorBoundary(
  EditHouseholdDataChange,
  'EditHouseholdDataChange',
);
