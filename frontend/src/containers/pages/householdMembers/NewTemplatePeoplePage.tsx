import moment from 'moment';
import {
  createPeriodicDataUpdateTemplate,
  fetchPeriodicFields,
} from '@api/periodicDataUpdateApi';
import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { FieldsToUpdate } from '@components/periodicDataUpdates/FieldsToUpdate';
import { FilterIndividuals } from '@components/periodicDataUpdates/FilterIndividuals';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, Step, StepLabel, Stepper } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { Formik } from 'formik';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';

export const NewTemplatePeoplePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();
  const { showMessage } = useSnackbar();

  const initialFilter = {
    registration_data_import_id: null,
    target_population_id: null,
    gender: '',
    ageFrom: '',
    ageTo: '',
    registrationDateFrom: '',
    registrationDateTo: '',
    hasGrievanceTicket: '',
    admin1: [],
    admin2: [],
    receivedAssistance: '',
  };

  const [filter, setFilter] = useState(initialFilter);

  const createTemplate = useMutation({
    mutationFn: (params: {
      businessAreaSlug: string;
      programId: string;
      //TODO MS: Add types
      roundsData: any;
      filters: any;
    }) =>
      createPeriodicDataUpdateTemplate(
        params.businessAreaSlug,
        params.programId,
        params.roundsData,
        params.filters,
      ),
    onSuccess: () => {
      showMessage(t('Template created successfully.'));
      navigate(`/${baseUrl}/population/people`, {
        state: { isNewTemplateJustCreated: true },
      });
    },
  });

  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Filter Individuals', 'Fields to Update'];

  const { data: periodicFieldsData, isLoading: periodicFieldsLoading } =
    useQuery({
      queryKey: ['periodicFields', businessArea, programId],
      queryFn: () => fetchPeriodicFields(businessArea, programId),
    });

  if (periodicFieldsLoading) {
    return <LoadingComponent />;
  }

  if (!periodicFieldsData) {
    return null;
  }

  const mapToInitialValuesRoundsData = (data) => {
    if (!data.results) {
      return [];
    }
    return data.results.map((item) => {
      const { name, pdu_data } = item;
      const { rounds_names } = pdu_data;

      return {
        field: name,
        rounds: rounds_names.map((_, roundIndex) => ({
          round: roundIndex + 1,
          round_name: rounds_names[roundIndex],
        })),
        numberOfRounds: rounds_names.length,
        roundNumber: 1,
        roundName: rounds_names[0],
      };
    });
  };

  const mappedRoundsData = mapToInitialValuesRoundsData(periodicFieldsData);

  const initialValues = {
    roundsData: mappedRoundsData,
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('People'),
      to: `/${baseUrl}/population/people`,
    },
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = (values) => {
    const filters = {
      registration_data_import_id: filter.registration_data_import_id,
      target_population_id: filter.target_population_id,
      gender: filter.gender,
      age: {
        from: Number(filter.ageFrom),
        to: Number(filter.ageTo),
      },
      registration_date: {
        from: moment(filter.registrationDateFrom).format('YYYY-MM-DD'),
        to: moment(filter.registrationDateTo).format('YYYY-MM-DD'),
      },
      has_grievance_ticket: filter.hasGrievanceTicket === 'YES' ? true : false,
      admin1: filter.admin1?.map((el) => el.value),
      admin2: filter.admin2?.map((el) => el.value),
      received_assistance: filter.receivedAssistance === 'YES' ? true : false,
    };

    const isEmpty = (value) => {
      if (value == null) return true;
      if (typeof value === 'string' && value.trim() === '') return true;
      if (Array.isArray(value) && value.length === 0) return true;
      if (
        typeof value === 'object' &&
        !Array.isArray(value) &&
        Object.keys(value).length === 0
      )
        return true;
      return false;
    };

    const filtersToSend = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => !isEmpty(value)),
    );

    const roundsDataToSend = values.roundsData
      .filter((el) => el.checked)
      .map((data) => ({
        field: data.field,
        round: data.roundNumber,
        round_name: data.roundName,
      }));

    const payload = {
      rounds_data: roundsDataToSend,
      filters: filtersToSend,
    };

    createTemplate.mutate({
      businessAreaSlug: businessArea,
      programId: programId,
      roundsData: payload.rounds_data,
      filters: payload.filters,
    });
  };

  return (
    <Formik initialValues={initialValues} onSubmit={handleSubmit}>
      {({ values, setFieldValue, submitForm }) => {
        const roundsDataToSend = values.roundsData
          .filter((el) => el.checked)
          .map((data) => ({
            field: data.field,
            round: data.roundNumber,
            round_name: data.roundName,
          }));

        return (
          <form onSubmit={handleSubmit}>
            <PageHeader
              title={t('New Template Page')}
              breadCrumbs={
                hasPermissions(
                  PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <BaseSection>
              <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((label) => (
                  <Step data-cy="label-key" key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
              {activeStep === 0 && (
                <FilterIndividuals
                  isOnPaper={false}
                  filter={filter}
                  setFilter={setFilter}
                />
              )}
              {activeStep === 1 && (
                <FieldsToUpdate values={values} setFieldValue={setFieldValue} />
              )}
              <Box
                display="flex"
                mt={4}
                justifyContent="flex-start"
                width="100%"
              >
                <Box mr={2}>
                  <Button
                    variant="outlined"
                    color="secondary"
                    component={Link}
                    to={`/${baseUrl}/population/people`}
                    data-cy="cancel-button"
                  >
                    Cancel
                  </Button>
                </Box>
                <Box display="flex">
                  {activeStep === 1 && (
                    <Box mr={2}>
                      <Button
                        data-cy="back-button"
                        variant="outlined"
                        onClick={handleBack}
                      >
                        Back
                      </Button>
                    </Box>
                  )}
                  <Box>
                    <Button
                      variant="contained"
                      color="primary"
                      data-cy="submit-button"
                      disabled={
                        activeStep === 1 && roundsDataToSend.length === 0
                      }
                      onClick={activeStep === 1 ? submitForm : handleNext}
                    >
                      {activeStep === 1 ? 'Generate Template' : 'Next'}
                    </Button>
                  </Box>
                </Box>
              </Box>
            </BaseSection>
          </form>
        );
      }}
    </Formik>
  );
};
