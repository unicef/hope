import { Box, Button, Grid2 as Grid, Typography } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllIndividualsQuery,
  useAllEditPeopleFieldsQuery,
  useIndividualLazyQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { EditPeopleDataChangeFieldRow } from './EditPeopleDataChangeFieldRow';
import { ExistingDocumentFieldArray } from '@components/grievances/EditIndividualDataChange/ExistingDocumentFieldArray';
import { NewDocumentFieldArray } from '@components/grievances/EditIndividualDataChange/NewDocumentFieldArray';
import { ExistingPaymentChannelFieldArray } from '../EditIndividualDataChange/ExistingPaymentChannelFieldArray';
import { NewPaymentChannelFieldArray } from '../EditIndividualDataChange/NewPaymentChannelFieldArray';
import withErrorBoundary from '@components/core/withErrorBoundary';

const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export interface EditPeopleDataChangeProps {
  values;
  setFieldValue;
  form;
  field;
}

function EditPeopleDataChange({
  values,
  setFieldValue,
}: EditPeopleDataChangeProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'] =
    values.selectedIndividual;
  const { data: editPeopleFieldsData, loading: editPeopleFieldsLoading } =
    useAllEditPeopleFieldsQuery();

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
  if (!individual) {
    return <div>{t('You have to select an individual earlier')}</div>;
  }
  if (
    editPeopleFieldsLoading ||
    fullIndividualLoading ||
    editPeopleFieldsLoading ||
    !fullIndividual
  ) {
    return <LoadingComponent />;
  }
  const notAvailableItems = (values.individualDataUpdateFields || []).map(
    (fieldItem) => fieldItem.fieldName,
  );

  return (
    <>
      {!isEditTicket && (
        <BoxWithBorders>
          <Title>
            <Typography variant="h6">{t('Bio Data')}</Typography>
          </Title>
          <FieldArray
            name="individualDataUpdateFields"
            render={(arrayHelpers) => (
              <>
                {values.individualDataUpdateFields.map((item, index) => (
                  <EditPeopleDataChangeFieldRow
                    // eslint-disable-next-line react/no-array-index-key
                    key={`${index}-${item?.fieldName}`}
                    itemValue={item}
                    index={index}
                    individual={fullIndividual.individual}
                    fields={editPeopleFieldsData.allEditPeopleFieldsAttributes}
                    notAvailableFields={notAvailableItems}
                    onDelete={() => arrayHelpers.remove(index)}
                    values={values}
                  />
                ))}
                <Grid size={{ xs: 4 }}>
                  <Button
                    color="primary"
                    onClick={() => {
                      arrayHelpers.push({ fieldName: null, fieldValue: '' });
                    }}
                    startIcon={<AddCircleOutline />}
                    data-cy="button-add-new-field"
                    disabled={isEditTicket}
                  >
                    {t('Add new field')}
                  </Button>
                </Grid>
              </>
            )}
          />
        </BoxWithBorders>
      )}
      <BoxWithBorders>
        <Box mt={3}>
          <Title>
            <Typography variant="h6">
              {t(
                'Documents: change/upload of document with other info (country, number etc.): add label beneficiary personal documents',
              )}
            </Typography>
          </Title>
          <ExistingDocumentFieldArray
            values={values}
            setFieldValue={setFieldValue}
            individual={fullIndividual.individual}
            addIndividualFieldsData={editPeopleFieldsData}
          />
          {!isEditTicket && (
            <NewDocumentFieldArray
              values={values}
              addIndividualFieldsData={editPeopleFieldsData}
              setFieldValue={setFieldValue}
            />
          )}
        </Box>
      </BoxWithBorders>
      <BoxWithBorders>
        <Box mt={3}>
          <Title>
            <Typography variant="h6">{t('Payment Channels')}</Typography>
          </Title>
          <ExistingPaymentChannelFieldArray
            values={values}
            setFieldValue={setFieldValue}
            individual={fullIndividual.individual}
          />
          {!isEditTicket && <NewPaymentChannelFieldArray values={values} />}
        </Box>
      </BoxWithBorders>
    </>
  );
}

export default withErrorBoundary(EditPeopleDataChange, 'EditPeopleDataChange');
