import withErrorBoundary from '@components/core/withErrorBoundary';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import {
  AllIndividualsQuery,
  useAllAddIndividualFieldsQuery,
} from '@generated/graphql';
import { AddCircleOutline } from '@mui/icons-material';
import { Box, Button, Grid2 as Grid, Typography } from '@mui/material';
import { FieldArray } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { EditIndividualDataChangeFieldRow } from './EditIndividualDataChangeFieldRow';
import { ExistingDocumentFieldArray } from './ExistingDocumentFieldArray';
import { ExistingIdentityFieldArray } from './ExistingIdentityFieldArray';
import { NewDocumentFieldArray } from './NewDocumentFieldArray';
import { NewIdentityFieldArray } from './NewIdentityFieldArray';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export interface EditIndividualDataChangeProps {
  values;
  setFieldValue;
  form;
  field;
}

function EditIndividualDataChange({
  values,
  setFieldValue,
}: EditIndividualDataChangeProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'] =
    values.selectedIndividual;
  const { data: addIndividualFieldsData, loading: addIndividualFieldsLoading } =
    useAllAddIndividualFieldsQuery({ fetchPolicy: 'network-only' });
  const { data: fullIndividual, isLoading: fullIndividualLoading } =
    useQuery<IndividualDetail>({
      queryKey: [
        'businessAreaProgramIndividual',
        businessArea,
        programId,
        individual?.id,
        values.selectedIndividual,
      ],
      queryFn: () =>
        RestService.restBusinessAreasProgramsIndividualsRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: individual?.id,
        }),
    });

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
    return (
      <div>
        {t(`You have to select a ${beneficiaryGroup?.memberLabel} earlier`)}
      </div>
    );
  }
  if (
    addIndividualFieldsLoading ||
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
                  <EditIndividualDataChangeFieldRow
                    // eslint-disable-next-line react/no-array-index-key
                    key={`${index}-${item?.fieldName}`}
                    itemValue={item}
                    index={index}
                    individual={fullIndividual}
                    fields={
                      addIndividualFieldsData.allAddIndividualsFieldsAttributes
                    }
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
            individual={fullIndividual}
            addIndividualFieldsData={addIndividualFieldsData}
          />
          {!isEditTicket && (
            <NewDocumentFieldArray
              values={values}
              addIndividualFieldsData={addIndividualFieldsData}
              setFieldValue={setFieldValue}
            />
          )}
        </Box>
      </BoxWithBorders>
      <BoxWithBorders>
        <Box mt={3}>
          <Title>
            <Typography variant="h6">{t('Identities')}</Typography>
          </Title>
          <ExistingIdentityFieldArray
            values={values}
            setFieldValue={setFieldValue}
            individual={fullIndividual}
            addIndividualFieldsData={addIndividualFieldsData}
          />
          {!isEditTicket && (
            <NewIdentityFieldArray
              values={values}
              addIndividualFieldsData={addIndividualFieldsData}
            />
          )}
        </Box>
      </BoxWithBorders>
      {/* //TODO: Uncomment when payment channels are available */}
      {/* <BoxWithBorders>
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
      </BoxWithBorders> */}
    </>
  );
}

export default withErrorBoundary(
  EditIndividualDataChange,
  'EditIndividualDataChange',
);
