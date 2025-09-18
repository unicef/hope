import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AddCircleOutline } from '@mui/icons-material';
import { Box, Button, Grid, Typography } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { FieldArray } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { EditPeopleDataChangeFieldRow } from './EditPeopleDataChangeFieldRow';
import { ExistingDocumentFieldArray } from '@components/grievances/EditIndividualDataChange/ExistingDocumentFieldArray';
import { NewDocumentFieldArray } from '@components/grievances/EditIndividualDataChange/NewDocumentFieldArray';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ExistingAccountsFieldArray } from '@components/grievances/EditIndividualDataChange/ExistingAccountsFieldArray';
import { NewAccountFieldArray } from '@components/grievances/EditIndividualDataChange/NewAccountFieldArray';

const BoxWithBorders = styled.div`
  border-bottom: 1px solid #d8d8d8;
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
  const { businessArea, programId } = useBaseUrl();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const individual: IndividualList = values.selectedIndividual;
  const { data: editPeopleFieldsData, isLoading: editPeopleFieldsLoading } =
    useQuery({
      queryKey: ['allEditPeopleFieldsAttributes', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsAllEditPeopleFieldsAttributesList(
          {
            businessAreaSlug: businessArea,
          },
        ),
    });

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['grievanceTicketsChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery({
      queryKey: ['individualsChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: countriesData, isLoading: countriesLoading } = useQuery({
    queryKey: ['countriesList'],
    queryFn: () => RestService.restChoicesCountriesList(),
  });

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
    return <div>{t('You have to select an individual earlier')}</div>;
  }
  if (
    editPeopleFieldsLoading ||
    fullIndividualLoading ||
    choicesLoading ||
    individualChoicesLoading ||
    countriesLoading ||
    !fullIndividual ||
    !editPeopleFieldsData
  ) {
    return (
      <div>
        <LoadingComponent />
      </div>
    );
  }

  const combinedData = {
    results: editPeopleFieldsData?.results || [],
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
          <FieldArray
            name="individualDataUpdateFields"
            render={(arrayHelpers) => (
              <>
                {values.individualDataUpdateFields.map((item, index) => (
                  <EditPeopleDataChangeFieldRow
                    key={`${index}-${item?.fieldName}`}
                    itemValue={item}
                    index={index}
                    individual={fullIndividual}
                    fields={combinedData.results}
                    notAvailableFields={notAvailableItems}
                    onDelete={() => arrayHelpers.remove(index)}
                    values={values}
                  />
                ))}
                <Grid size={4}>
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

export default withErrorBoundary(EditPeopleDataChange, 'EditPeopleDataChange');
