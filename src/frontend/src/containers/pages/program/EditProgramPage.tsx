import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import {
  editPartnersValidationSchema,
  editProgramDetailsValidationSchema,
} from '@components/programs/CreateProgram/editProgramValidationSchema';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';
import { DetailsStep } from '@components/programs/EditProgram/DetailsStep';
import { PartnersStep } from '@components/programs/EditProgram/PartnersStep';
import { ProgramFieldSeriesStep } from '@components/programs/EditProgram/ProgramFieldSeriesStep';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Fade } from '@mui/material';
import { PaginatedAreaTreeList } from '@restgenerated/models/PaginatedAreaTreeList';
import { PartnerAccessEnum } from '@restgenerated/models/PartnerAccessEnum';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ProgramUpdate } from '@restgenerated/models/ProgramUpdate';
import { ProgramUpdatePartnerAccess } from '@restgenerated/models/ProgramUpdatePartnerAccess';
import { UserChoices } from '@restgenerated/models/UserChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  decodeIdString,
  isPartnerVisible,
  mapPartnerChoicesWithoutUnicef,
  showApiErrorMessages,
  deepUnderscore,
} from '@utils/utils';
import { Formik } from 'formik';
import { omit } from 'lodash';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { hasPermissionInModule } from '../../../config/permissions';

const EditProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const location = useLocation();
  const option = location.state?.option;

  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: treeData, isLoading: treeLoading } =
    useQuery<PaginatedAreaTreeList>({
      queryKey: ['allAreasTree', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGeoAreasAllAreasTreeList({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: program, isLoading: loadingProgram } = useQuery<ProgramDetail>({
    queryKey: ['businessAreaProgram', businessArea, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        slug: id,
      }),
  });

  const { data: userPartnerChoicesData, isLoading: userPartnerChoicesLoading } =
    useQuery<UserChoices>({
      queryKey: ['userChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasUsersChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<ProgramChoices>({
      queryKey: ['programChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasProgramsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
      staleTime: 1000 * 60 * 10,
      gcTime: 1000 * 60 * 30,
    });

  const queryClient = useQueryClient();

  const { mutateAsync: updateProgramDetails } = useMutation({
    mutationFn: (programData: ProgramUpdate) => {
      return RestService.restBusinessAreasProgramsUpdate({
        businessAreaSlug: businessArea,
        slug: id,
        requestBody: programData,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['businessAreaProgram', businessArea, id],
      });
      await queryClient.invalidateQueries({
        queryKey: ['businessAreaPrograms', businessArea],
      });
    },
  });

  const {
    mutateAsync: updateProgramPartners,
    isPending: loadingPartnersUpdate,
  } = useMutation({
    mutationFn: (partnerData: ProgramUpdatePartnerAccess) => {
      return RestService.restBusinessAreasProgramsUpdatePartnerAccessCreate({
        businessAreaSlug: businessArea,
        slug: id,
        requestBody: partnerData,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['businessAreaProgram', businessArea, id],
      });
      await queryClient.invalidateQueries({
        queryKey: ['businessAreaPrograms', businessArea],
      });
      // Invalidate activity logs cache
      await queryClient.invalidateQueries({
        queryKey: ['activityLogs', businessArea, decodeIdString(id)],
      });
    },
  });

  if (
    loadingProgram ||
    treeLoading ||
    userPartnerChoicesLoading ||
    choicesLoading
  )
    return <LoadingComponent />;

  if (!program || !treeData || !userPartnerChoicesData || !choicesData)
    return null;

  const {
    name,
    programmeCode,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    beneficiaryGroup,
    description,
    budget = '',
    administrativeAreasOfImplementation,
    populationGoal = '',
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    version,
    partners,
    partnerAccess = 'ALL_PARTNERS_ACCESS',
    registrationImportsTotalCount,
    pduFields,
    targetPopulationsCount,
  } = program;

  const programHasRdi = registrationImportsTotalCount > 0;
  const programHasTp = targetPopulationsCount > 0;

  const handleSubmitProgramDetails = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : '0.00';
    const populationGoalValue = parseInt(values.populationGoal, 10) ?? 0;
    const populationGoalParsed = !Number.isNaN(populationGoalValue)
      ? populationGoalValue
      : 0;

    const pduFieldsToSend = values.pduFields
      .filter((item) => item.label !== '')
      .map(({ pdu_data, ...rest }) => {
        let newPduData = pdu_data;
        if (pdu_data) {
          const filteredPduData = Object.fromEntries(
            Object.entries(pdu_data).filter(([key]) => key !== 'id'),
          );
          filteredPduData.rounds_names = (() => {
            if (!pdu_data.rounds_names) {
              pdu_data.rounds_names = [];
            }
            if (
              pdu_data.number_of_rounds === 1 &&
              pdu_data.rounds_names.length === 0
            ) {
              return [''];
            }
            return pdu_data.rounds_names.map((roundName) => roundName || '');
          })();
          newPduData = filteredPduData;
        }
        return {
          ...rest,
          pduData: newPduData,
        };
      });

    try {
      const requestValuesDetails = omit(values, [
        'editMode',
        'partners',
        'partnerAccess',
        'pduFields',
      ]);

      // Build the base programData object
      const programData: ProgramUpdate = {
        programmeCode: requestValuesDetails.programmeCode,
        name: requestValuesDetails.name,
        slug: '', // readonly field, will be ignored by API
        sector: requestValuesDetails.sector,
        description: requestValuesDetails.description,
        budget: budgetToFixed,
        administrativeAreasOfImplementation:
          requestValuesDetails.administrativeAreasOfImplementation,
        populationGoal: populationGoalParsed,
        cashPlus: requestValuesDetails.cashPlus,
        frequencyOfPayments: requestValuesDetails.frequencyOfPayments,
        // Always send dataCollectingType, but only update if Draft
        dataCollectingType:
          program.status === 'DRAFT'
            ? requestValuesDetails.dataCollectingTypeCode
            : program.dataCollectingType.code,
        beneficiaryGroup: requestValuesDetails.beneficiaryGroup,
        startDate: requestValuesDetails.startDate,
        endDate:
          requestValuesDetails.endDate === '' ||
          requestValuesDetails.endDate === undefined
            ? null
            : requestValuesDetails.endDate,
        pduFields: deepUnderscore(pduFieldsToSend),
        version,
        status: '', // readonly field, will be ignored by API
        partnerAccess: '', // readonly field, will be ignored by API
      };

      const response = await updateProgramDetails(programData);
      showMessage(t('Programme edited.'));
      navigate(`/${baseUrl}/details/${response.slug}`);
    } catch (e: any) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const handleSubmitPartners = async (values): Promise<void> => {
    const partnersToSet =
      values.partnerAccess === 'SELECTED_PARTNERS_ACCESS'
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
          }))
        : [];

    try {
      const partnerData: ProgramUpdatePartnerAccess = {
        partners: partnersToSet,
        partnerAccess: values.partnerAccess as PartnerAccessEnum,
        version,
      };

      await updateProgramPartners(partnerData);
      showMessage(t('Programme Partners updated.'));
      navigate(`/${baseUrl}/details/${id}`);
    } catch (e: any) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const initialValuesProgramDetails = {
    editMode: true,
    name,
    programmeCode: programmeCode,
    startDate: startDate,
    endDate: endDate,
    sector,
    dataCollectingTypeCode: dataCollectingType.code,
    beneficiaryGroup: beneficiaryGroup.id,
    description,
    budget,
    administrativeAreasOfImplementation: administrativeAreasOfImplementation,
    populationGoal: populationGoal,
    cashPlus: cashPlus,
    frequencyOfPayments: frequencyOfPayments,
    pduFields: pduFields,
  };

  initialValuesProgramDetails.budget =
    program.budget === '0.00' ? '' : program.budget;
  initialValuesProgramDetails.populationGoal =
    program.populationGoal === 0 ? '' : program.populationGoal;

  const initialValuesPartners = {
    partners:
      partners.length > 0
        ? partners
            .filter((partner) => isPartnerVisible(partner.name))
            .map((partner) => ({
              id: partner.id,
              areaAccess: partner.areaAccess,
              areas: Array.isArray(partner.areas)
                ? partner.areas.map((area) => area.id)
                : [],
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
      'beneficiaryGroup',
      'description',
      'budget',
      'administrativeAreasOfImplementation',
      'populationGoal',
      'cashPlus',
      'frequencyOfPayments',
    ],
    ['partnerAccess'],
  ];

  const { partnerChoicesTemp: userPartnerChoices } = userPartnerChoicesData;

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
          validationSchema={editProgramDetailsValidationSchema(t)}
          validationContext={{ isEdit: true }}
          validateOnChange={true}
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
                            programHasRdi={programHasRdi}
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
                            pdusubtypeChoicesData={
                              choicesData?.pduSubtypeChoices
                            }
                            programHasRdi={programHasRdi}
                            programHasTp={programHasTp}
                            programId={id}
                            program={program}
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
            const mappedPartnerChoices = mapPartnerChoicesWithoutUnicef(
              userPartnerChoices,
              values.partners,
            );

            return (
              <BaseSection title={t('Programme Partners')}>
                <Fade in={option === 'partners'} timeout={600}>
                  <div>
                    <PartnersStep
                      values={values}
                      allAreasTreeData={treeData || []}
                      partnerChoices={mappedPartnerChoices}
                      submitForm={submitForm}
                      setFieldValue={setFieldValue}
                      programId={id}
                      loading={loadingPartnersUpdate}
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
export default withErrorBoundary(EditProgramPage, 'EditProgramPage');
