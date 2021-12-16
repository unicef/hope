import { Button, Grid, Typography } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllHouseholdsQuery,
  useAllEditHouseholdFieldsQuery,
  useHouseholdLazyQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../LoadingComponent';
import { EditHouseholdDataChangeFieldRow } from './EditHouseholdDataChangeFieldRow';

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;

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
