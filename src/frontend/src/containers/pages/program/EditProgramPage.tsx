import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/EditProgram/DetailsStep';
import { PartnersStep } from '@components/programs/EditProgram/PartnersStep';
import { ProgramFieldSeriesStep } from '@components/programs/EditProgram/ProgramFieldSeriesStep';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';
import {
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  usePduSubtypeChoicesDataQuery,
  useProgramQuery,
  useUpdateProgramMutation,
  useUpdateProgramPartnersMutation,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Fade } from '@mui/material';
import { decodeIdString } from '@utils/utils';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { hasPermissionInModule } from '../../../config/permissions';
import {
  editPartnersValidationSchema,
  editProgramDetailsValidationSchema,
} from '@components/programs/CreateProgram/editProgramValidationSchema';

export const EditProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const location = useLocation();
  const option = location.state?.option;

  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const { data, loading: loadingProgram } = useProgramQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const { data: pdusubtypeChoicesData, loading: pdusubtypeChoicesLoading } =
    usePduSubtypeChoicesDataQuery();

  const [updateProgramDetails] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(id),
          count: 5,
          businessArea,
        },
      },
    ],
  });

  const [updateProgramPartners] = useUpdateProgramPartnersMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(id),
          count: 5,
          businessArea,
        },
      },
    ],
  });

  if (
    loadingProgram ||
    treeLoading ||
    userPartnerChoicesLoading ||
    pdusubtypeChoicesLoading
  )
    return <LoadingComponent />;

  if (!data || !treeData || !userPartnerChoicesData || !pdusubtypeChoicesData)
    return null;

  const {
    name,
    programmeCode,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    description,
    budget = '',
    administrativeAreasOfImplementation,
    populationGoal = '',
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    version,
    partners,
    partnerAccess = ProgramPartnerAccess.AllPartnersAccess,
    registrationImports,
    pduFields,
    targetPopulationsCount,
  } = data.program;

  const programHasRdi = registrationImports?.totalCount > 0;
  const programHasTp = targetPopulationsCount > 0;

  const handleSubmitProgramDetails = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : 0;
    const populationGoalValue = parseInt(values.populationGoal, 10) ?? 0;
    const populationGoalParsed = !Number.isNaN(populationGoalValue)
      ? populationGoalValue
      : 0;

    const pduFieldsToSend = values.pduFields
      .filter((item) => item.label !== '')
      .map(({ __typename, pduData, ...rest }) => ({
        ...rest,
        pduData: pduData
          ? {
              ...Object.fromEntries(
                Object.entries(pduData).filter(
                  ([key]) => key !== '__typename' && key !== 'id',
                ),
              ),
              roundsNames: (() => {
                if (!pduData.roundsNames) {
                  pduData.roundsNames = [];
                }

                if (
                  pduData.numberOfRounds === 1 &&
                  pduData.roundsNames.length === 0
                ) {
                  return [''];
                }

                return pduData.roundsNames.map((roundName) => roundName || '');
              })(),
            }
          : pduData,
      }));

    try {
      const {
        editMode,
        partners: _partners,
        partnerAccess: _partnerAccess,
        pduFields: _pduFields,
        ...requestValuesDetails
      } = values;

      const response = await updateProgramDetails({
        variables: {
          programData: {
            id,
            ...requestValuesDetails,
            budget: budgetToFixed,
            populationGoal: populationGoalParsed,
            pduFields: pduFieldsToSend,
          },
          version,
        },
      });
      showMessage(t('Programme edited.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleSubmitPartners = async (values): Promise<void> => {
    const partnersToSet =
      values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];

    try {
      const response = await updateProgramPartners({
        variables: {
          programData: {
            id,
            partners: partnersToSet,
            partnerAccess: values.partnerAccess,
          },
          version,
        },
      });
      showMessage(t('Programme Partners updated.'));
      navigate(
        `/${baseUrl}/details/${response.data.updateProgramPartners.program.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const mappedPduFields = Object.entries(pduFields).map(([, field]) => {
    const { ...rest } = field;
    return {
      ...rest,
      label: JSON.parse(field.label)['English(EN)'],
    };
  });

  const initialValuesProgramDetails = {
    editMode: true,
    name,
    programmeCode,
    startDate,
    endDate,
    sector,
    dataCollectingTypeCode: dataCollectingType?.code,
    description,
    budget,
    administrativeAreasOfImplementation,
    populationGoal,
    cashPlus,
    frequencyOfPayments,
    pduFields: mappedPduFields,
  };

  initialValuesProgramDetails.budget =
    data.program.budget === '0.00' ? '' : data.program.budget;
  initialValuesProgramDetails.populationGoal =
    data.program.populationGoal === 0 ? '' : data.program.populationGoal;

  const initialValuesPartners = {
    partners:
      partners.length > 0
        ? partners
            .filter((partner) => partner.name !== 'UNICEF')
            .map((partner) => ({
              id: partner.id,
              areas: partner.areas.map((area) => decodeIdString(area.id)),
              areaAccess: partner.areaAccess,
            }))
        : [],
    partnerAccess,
  };

  const stepFields = [
    [
      'name',
      'programmeCode',
      'startDate',
      'endDate',
      'sector',
      'dataCollectingTypeCode',
      'description',
      'budget',
      'administrativeAreasOfImplementation',
      'populationGoal',
      'cashPlus',
      'frequencyOfPayments',
    ],
    ['partnerAccess'],
  ];

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme'),
      to: `/${baseUrl}/details/${id}`,
    },
  ];
  const stepsData = [
    {
      title: t('Details'),
      description: t(
        'To create a new Programme, please complete all required fields on the form below and save.',
      ),
      dataCy: 'step-button-details',
    },
    {
      title: t('Programme Time Series Fields'),
      description: t(
        'The Time Series Fields feature allows serial updating of individual data through an XLSX file.',
      ),
      dataCy: 'step-button-time-series-fields',
    },
  ];

  return (
    <>
      <PageHeader
        title={`${t('Edit Programme')}: (${name})`}
        breadCrumbs={
          hasPermissionInModule('PROGRAMME_VIEW_LIST_AND_DETAILS', permissions)
            ? breadCrumbsItems
            : null
        }
      />
      {option === 'details' && (
        <Formik
          initialValues={initialValuesProgramDetails}
          onSubmit={(values) => {
            handleSubmitProgramDetails(values);
          }}
          validationSchema={editProgramDetailsValidationSchema(
            t,
            initialValuesProgramDetails,
          )}
        >
          {({
            submitForm,
            values,
            validateForm,
            setFieldTouched,
            setFieldValue,
            errors,
            setErrors,
          }) => {
            const handleNextStep = async () => {
              await handleNext({
                validateForm,
                stepFields,
                step,
                setStep,
                setFieldTouched,
                values,
                setErrors,
              });
            };
            return (
              <BaseSection
                title={stepsData[step].title}
                description={stepsData[step].description}
                stepper={
                  <ProgramStepper
                    step={step}
                    setStep={setStep}
                    stepsData={stepsData}
                  />
                }
              >
                <Box p={3}>
                  <>
                    <Fade in={step === 0} timeout={600}>
                      <div>
                        {step === 0 && (
                          <DetailsStep
                            values={values}
                            handleNext={handleNextStep}
                            programId={id}
                            errors={errors}
                          />
                        )}
                      </div>
                    </Fade>
                    <Fade in={step === 1} timeout={600}>
                      <div>
                        {step === 1 && (
                          <ProgramFieldSeriesStep
                            values={values}
                            step={step}
                            setStep={setStep}
                            pdusubtypeChoicesData={pdusubtypeChoicesData}
                            programHasRdi={programHasRdi}
                            programHasTp={programHasTp}
                            programId={id}
                            program={data.program}
                            setFieldValue={setFieldValue}
                            submitForm={submitForm}
                          />
                        )}
                      </div>
                    </Fade>
                  </>
                </Box>
              </BaseSection>
            );
          }}
        </Formik>
      )}
      {option === 'partners' && (
        <Formik
          initialValues={initialValuesPartners}
          onSubmit={(values) => {
            handleSubmitPartners(values);
          }}
          validationSchema={editPartnersValidationSchema(t)}
        >
          {({ submitForm, values, setFieldValue }) => {
            const mappedPartnerChoices = userPartnerChoices
              .filter((partner) => partner.name !== 'UNICEF')
              .map((partner) => ({
                value: partner.value,
                label: partner.name,
                disabled: values.partners.some((p) => p.id === partner.value),
              }));

            return (
              <BaseSection title={t('Programme Partners')}>
                <Fade in={option === 'partners'} timeout={600}>
                  <div>
                    <PartnersStep
                      values={values}
                      allAreasTreeData={allAreasTree}
                      partnerChoices={mappedPartnerChoices}
                      submitForm={submitForm}
                      setFieldValue={setFieldValue}
                      programId={id}
                    />
                  </div>
                </Fade>
              </BaseSection>
            );
          }}
        </Formik>
      )}
    </>
  );
};
