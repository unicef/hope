import { Box, Button, Grid, Typography } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllIndividualsQuery,
  useAllAddIndividualFieldsQuery,
  useIndividualLazyQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../LoadingComponent';
import { ExistingDocumentFieldArray } from './ExistingDocumentFieldArray';
import { ExistingIdentityFieldArray } from './ExistingIdentityFieldArray';
import { NewDocumentFieldArray } from './NewDocumentFieldArray';
import { NewIdentityFieldArray } from './NewIdentityFieldArray';
import { EditIndividualDataChangeFieldRow } from './EditIndividualDataChangeFieldRow';

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

export interface EditIndividualDataChangeProps {
  values;
  setFieldValue;
  form;
  field;
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
                      values={values}
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
          addIndividualFieldsData={addIndividualFieldsData}
        />
        <NewDocumentFieldArray
          values={values}
          addIndividualFieldsData={addIndividualFieldsData}
          setFieldValue={setFieldValue}
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
          addIndividualFieldsData={addIndividualFieldsData}
        />
        <NewIdentityFieldArray
          values={values}
          addIndividualFieldsData={addIndividualFieldsData}
        />
      </Box>
    </>
  );
};
