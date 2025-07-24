import { Box, Button, Grid2 as Grid, Typography } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { EditIndividualDataChangeFieldRow } from './EditIndividualDataChangeFieldRow';
import { ExistingDocumentFieldArray } from './ExistingDocumentFieldArray';
import { ExistingIdentityFieldArray } from './ExistingIdentityFieldArray';
import { NewDocumentFieldArray } from './NewDocumentFieldArray';
import { NewIdentityFieldArray } from './NewIdentityFieldArray';
import { useProgramContext } from 'src/programContext';
import { ExistingAccountsFieldArray } from './ExistingAccountsFieldArray';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { NewAccountFieldArray } from '@components/grievances/EditIndividualDataChange/NewAccountFieldArray';

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
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const individual: IndividualList = values.selectedIndividual;
  const {
    data: addIndividualFieldsData,
    isLoading: addIndividualFieldsLoading,
  } = useQuery({
    queryKey: ['allAddIndividualsFieldsAttributes', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug,
        },
      ),
  });

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['grievanceTicketsChoices', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug,
      }),
  });

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery({
      queryKey: ['individualsChoices', businessAreaSlug],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug,
        }),
    });

  const { data: countriesData, isLoading: countriesLoading } = useQuery({
    queryKey: ['countriesList'],
    queryFn: () => RestService.restChoicesCountriesList(),
  });

  const { data: fullIndividual, isLoading: fullIndividualLoading } = useQuery({
    queryKey: ['individual', businessAreaSlug, programSlug, individual?.id],
    queryFn: () => {
      if (!individual?.id) return null;
      return RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug,
        programSlug,
        id: individual.id,
      });
    },
    enabled:
      !!individual?.id &&
      !!businessAreaSlug &&
      !!programSlug &&
      programSlug !== 'all',
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
    choicesLoading ||
    individualChoicesLoading ||
    countriesLoading ||
    !fullIndividual ||
    !addIndividualFieldsData
  ) {
    return <LoadingComponent />;
  }

  const combinedData = {
    allAddIndividualsFieldsAttributes: addIndividualFieldsData || [],
    countriesChoices: countriesData || [],
    documentTypeChoices: choicesData?.documentTypeChoices || [],
    identityTypeChoices: individualChoicesData?.identityTypeChoices || [],
  };
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
          <Grid container spacing={3}>
            <FieldArray
              name="individualDataUpdateFields"
              render={(arrayHelpers) => (
                <>
                  {values.individualDataUpdateFields.map((item, index) => (
                    <Grid size={{ xs: 12 }} key={`${index}-${item?.fieldName}`}>
                      <EditIndividualDataChangeFieldRow
                        itemValue={item}
                        index={index}
                        individual={fullIndividual}
                        fields={combinedData.allAddIndividualsFieldsAttributes}
                        notAvailableFields={notAvailableItems}
                        onDelete={() => arrayHelpers.remove(index)}
                        values={values}
                      />
                    </Grid>
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
          </Grid>
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
            addIndividualFieldsData={combinedData}
          />
          {!isEditTicket && (
            <NewDocumentFieldArray
              values={values}
              addIndividualFieldsData={combinedData}
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
            addIndividualFieldsData={combinedData}
          />
          {!isEditTicket && (
            <NewIdentityFieldArray
              values={values}
              addIndividualFieldsData={combinedData}
            />
          )}
        </Box>
      </BoxWithBorders>
      <BoxWithBorders>
        <Box mt={3}>
          <Title>
            <Typography variant="h6">{t('Accounts')}</Typography>
          </Title>
          <ExistingAccountsFieldArray
            values={values}
            setFieldValue={setFieldValue}
            individual={fullIndividual}
            individualChoicesData={individualChoicesData}
          />
          {!isEditTicket && (
            <NewAccountFieldArray
              values={values}
              individualChoicesData={individualChoicesData}
            />
          )}
        </Box>
      </BoxWithBorders>
    </>
  );
}

export default withErrorBoundary(
  EditIndividualDataChange,
  'EditIndividualDataChange',
);
