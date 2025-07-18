import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { AndDivider, AndDividerLabel } from '@components/targeting/AndDivider';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AddCircleOutline } from '@mui/icons-material';
import {
  Box,
  Button,
  Collapse,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  Tooltip,
  Typography,
} from '@mui/material';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import {
  chooseFieldType,
  clearField,
  formatCriteriaCollectorsFiltersBlocks,
  formatCriteriaFilters,
  formatCriteriaIndividualsFiltersBlocks,
  HhIdValidation,
  IndIdValidation,
  mapCriteriaToInitialValues,
  validate,
} from '@utils/targetingUtils';
import { Field, FieldArray, Formik } from 'formik';
import {
  Component,
  ReactElement,
  ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import * as Yup from 'yup';
import { DialogContainer } from '../dialogs/DialogContainer';
import { DialogDescription } from '../dialogs/DialogDescription';
import { DialogFooter } from '../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../dialogs/DialogTitleWrapper';
import { TargetingCriteriaCollectorFilterBlocks } from './TargetingCriteriaCollectorFilterBlocks';
import { TargetingCriteriaHouseholdFilter } from './TargetingCriteriaHouseholdFilter';
import { TargetingCriteriaIndividualFilterBlocks } from './TargetingCriteriaIndividualFilterBlocks';
import { useConfirmation } from '@components/core/ConfirmationDialog';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { PaginatedCollectorAttributeList } from '@restgenerated/models/PaginatedCollectorAttributeList';
import { FspChoices } from '@restgenerated/models/FspChoices';

const ButtonBox = styled.div`
  width: 300px;
`;
const DialogError = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: ${({ theme }) => theme.palette.error.dark};
`;

const StyledBox = styled(Box)`
  width: 100%;
`;

const requiredSchema = Yup.object().shape({
  deliveryMechanism: Yup.string().required('Delivery Mechanism is required'),
  fsp: Yup.string().required('FSP is required'),
  householdIds: HhIdValidation,
  individualIds: IndIdValidation,
  filters: Yup.array().of(
    Yup.object().shape({
      fieldName: Yup.string().required('Field Type is required'),
    }),
  ),
  individualsFiltersBlocks: Yup.array().of(
    Yup.object().shape({
      individualBlockFilters: Yup.array().of(
        Yup.object().shape({
          fieldName: Yup.string().required('Field Type is required'),
          fieldAttribute: Yup.object().shape({
            type: Yup.string().required(),
          }),
          roundNumber: Yup.string()
            .nullable()
            .when(
              ['fieldName', 'fieldAttribute'],
              (_fieldName, _fieldAttribute, schema) => {
                const parent = schema.parent;
                if (
                  parent &&
                  parent.fieldAttribute &&
                  parent.fieldAttribute?.type === 'PDU'
                ) {
                  return Yup.string().required('Round Number is required');
                }
                return Yup.string().notRequired();
              },
            ),
        }),
      ),
    }),
  ),
  collectorsFiltersBlocks: Yup.array().of(
    Yup.object().shape({
      collectorBlockFilters: Yup.array().of(
        Yup.object().shape({
          fieldName: Yup.string().required('Field Type is required'),
          value: Yup.string().required('Field Value is required'),
        }),
      ),
    }),
  ),
});

const optionalSchema = Yup.object().shape({
  deliveryMechanism: Yup.string(),
  fsp: Yup.string(),
  householdIds: HhIdValidation,
  individualIds: IndIdValidation,
  filters: Yup.array().of(
    Yup.object().shape({
      fieldName: Yup.string().required('Field Type is required'),
    }),
  ),
  individualsFiltersBlocks: Yup.array().of(
    Yup.object().shape({
      individualBlockFilters: Yup.array().of(
        Yup.object().shape({
          fieldName: Yup.string().required('Field Type is required'),
          fieldAttribute: Yup.object().shape({
            type: Yup.string().required(),
          }),
          roundNumber: Yup.string()
            .nullable()
            .when(
              ['fieldName', 'fieldAttribute'],
              (_fieldName, _fieldAttribute, schema) => {
                const parent = schema.parent;
                if (
                  parent &&
                  parent.fieldAttribute &&
                  parent.fieldAttribute?.type === 'PDU'
                ) {
                  return Yup.string().required('Round Number is required');
                }
                return Yup.string().notRequired();
              },
            ),
        }),
      ),
    }),
  ),
  collectorsFiltersBlocks: Yup.array().of(
    Yup.object().shape({
      collectorBlockFilters: Yup.array().of(
        Yup.object().shape({
          fieldName: Yup.string().required('Field Type is required'),
          value: Yup.string().required('Field Value is required'),
        }),
      ),
    }),
  ),
});

interface ArrayFieldWrapperProps {
  arrayHelpers;
  children: ReactNode;
}
class ArrayFieldWrapper extends Component<ArrayFieldWrapperProps, any> {
  getArrayHelpers(): object {
    const { arrayHelpers } = this.props;
    return arrayHelpers;
  }

  render(): ReactNode {
    const { children } = this.props;
    return children;
  }
}

interface TargetingCriteriaFormPropTypes {
  criteria?;
  addCriteria: (values) => void;
  open: boolean;
  onClose: () => void;
  individualFiltersAvailable: boolean;
  householdFiltersAvailable: boolean;
  collectorsFiltersAvailable: boolean;
  isSocialWorkingProgram: boolean;
  criteriaIndex: number;
}

const associatedWith = (type) => (item) => item.associatedWith === type;
const isNot = (type) => (item) => item?.type !== type;

export const TargetingCriteriaForm = ({
  criteria,
  addCriteria,
  open,
  onClose,
  individualFiltersAvailable,
  householdFiltersAvailable,
  collectorsFiltersAvailable,
  isSocialWorkingProgram,
  criteriaIndex,
}: TargetingCriteriaFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();

  const confirm = useConfirmation();
  const confirmationText = t(
    'Are you sure you want to ‘Lock’ TP without validating FSP and Delivery Mechanism requirements? This might result in individuals’ exclusion at later stages.',
  );
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: allCollectorFieldsAttributesData } =
    useQuery<PaginatedCollectorAttributeList>({
      queryKey: ['collectorFieldsAttributes'],
      queryFn: () =>
        RestService.restBusinessAreasAllCollectorFieldsAttributesList({}),
      staleTime: 5 * 60 * 1000, // 5 minutes - equivalent to cache-first policy
    });
  const { data: availableFspsForDeliveryMechanismData } = useQuery<
    FspChoices[]
  >({
    queryKey: [
      'businessAreasAvailableFspsForDeliveryMechanismsList',
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasAvailableFspsForDeliveryMechanismsList({
        businessAreaSlug: businessArea,
      }),
  });
  const { data, isLoading: loading } = useQuery({
    queryKey: ['businessAreasAllFieldsAttributesList'],
    queryFn: () => RestService.restBusinessAreasAllFieldsAttributesList({}),
    staleTime: 5 * 60 * 1000, // 5 minutes - equivalent to cache-first policy
  });

  const householdsFiltersBlocksWrapperRef = useRef(null);
  const individualsFiltersBlocksWrapperRef = useRef(null);
  const collectorsFiltersBlocksWrapperRef = useRef(null);
  const initialValue = mapCriteriaToInitialValues(criteria);
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const [allDataChoicesDict, setAllDataChoicesDict] = useState(null);
  const [allCollectorFieldsChoicesDict, setAllCollectorFieldsChoicesDict] =
    useState(null);

  const [openPaymentChannelCollapse, setOpenPaymentChannelCollapse] = useState(
    !!initialValue.deliveryMechanism,
  );

  useEffect(() => {
    setOpenPaymentChannelCollapse(!!initialValue.deliveryMechanism);
  }, [initialValue.deliveryMechanism]);

  const handlePaymentChannelButtonClick = () => {
    setOpenPaymentChannelCollapse(!openPaymentChannelCollapse);
  };

  const filteredIndividualData = useMemo(
    () => ({
      allFieldsAttributes: data
        //@ts-ignore
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    }),
    [data],
  );

  const filteredHouseholdData = useMemo(
    () => ({
      //@ts-ignore
      allFieldsAttributes: data?.filter(associatedWith('Household')),
    }),
    [data],
  );

  const allDataChoicesDictTmp = useMemo(
    () =>
      // @ts-ignore
      data?.reduce((acc, item) => {
        acc[item.name] = item.choices;
        return acc;
      }, {}),
    [data],
  );

  const allCollectorFieldsChoicesDictTmp = useMemo(
    () =>
      // @ts-ignore
      allCollectorFieldsAttributesData?.reduce((acc, item) => {
        acc[item.name] = item.choices;
        return acc;
      }, {}),
    [allCollectorFieldsAttributesData],
  );

  useEffect(() => {
    setIndividualData(filteredIndividualData);
    setHouseholdData(filteredHouseholdData);
    setAllDataChoicesDict(allDataChoicesDictTmp);
    setAllCollectorFieldsChoicesDict(allCollectorFieldsChoicesDictTmp);
  }, [
    filteredIndividualData,
    filteredHouseholdData,
    allDataChoicesDictTmp,
    allCollectorFieldsChoicesDictTmp,
  ]);

  if (!data || !allCollectorFieldsAttributesData) return null;

  const handleSubmit = (values, bag): void => {
    const householdsFiltersBlocks = formatCriteriaFilters(
      values.householdsFiltersBlocks,
    );
    const individualIds = values.individualIds;
    const householdIds = values.householdIds;
    const deliveryMechanism = values.deliveryMechanism;
    const fsp = values.fsp;
    const individualsFiltersBlocks = formatCriteriaIndividualsFiltersBlocks(
      values.individualsFiltersBlocks,
    );
    const collectorsFiltersBlocks = formatCriteriaCollectorsFiltersBlocks(
      values.collectorsFiltersBlocks,
    );

    addCriteria({
      householdsFiltersBlocks,
      individualsFiltersBlocks,
      collectorsFiltersBlocks,
      individualIds,
      householdIds,
      deliveryMechanism,
      fsp,
    });
    return bag.resetForm();
  };

  const validationSchema =
    criteriaIndex === 0 && openPaymentChannelCollapse
      ? requiredSchema
      : optionalSchema;

  if (loading || !open || !availableFspsForDeliveryMechanismData) return null;

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={handleSubmit}
        validate={(values) => validate(values, beneficiaryGroup)}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values, resetForm, setFieldValue, errors }) => {
          const fsps = availableFspsForDeliveryMechanismData || [];
          const mappedDeliveryMechanisms = fsps.map((el) => ({
            name: el.deliveryMechanism.name,
            value: el.deliveryMechanism.code,
          }));
          const mappedFsps =
            fsps
              .find(
                (el) => el.deliveryMechanism.code === values.deliveryMechanism,
              )
              ?.fsps.map((el) => ({ name: el.name, value: el.id })) || [];

          return (
            <Dialog
              open={open}
              onClose={onClose}
              scroll="paper"
              aria-labelledby="form-dialog-title"
              fullWidth
              maxWidth="md"
            >
              {open && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle component="div">
                  <Typography data-cy="title-add-filter" variant="h6">
                    {t('Add Filter')}
                  </Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                {
                  // @ts-ignore
                  errors.nonFieldErrors && (
                    <DialogError>
                      <ul>
                        {
                          // @ts-ignore
                          errors.nonFieldErrors.map((message) => (
                            <li key={message}>{message}</li>
                          ))
                        }
                      </ul>
                    </DialogError>
                  )
                }
                <DialogDescription>
                  {isSocialWorkingProgram
                    ? ''
                    : `All rules defined below have to be true for the entire ${beneficiaryGroup?.groupLabelPlural}.`}{' '}
                </DialogDescription>
                <Grid container spacing={3}>
                  {householdFiltersAvailable && (
                    <Grid size={{ xs: 12 }}>
                      <Field
                        data-cy="input-included-household-ids"
                        name="householdIds"
                        fullWidth
                        multiline
                        variant="outlined"
                        label={t(`${beneficiaryGroup?.groupLabelPlural} IDs`)}
                        component={FormikTextField}
                      />
                    </Grid>
                  )}
                  {householdFiltersAvailable && individualFiltersAvailable && (
                    <Grid size={{ xs: 12 }}>
                      <AndDivider>
                        <AndDividerLabel>AND</AndDividerLabel>
                      </AndDivider>
                    </Grid>
                  )}
                </Grid>
                <FieldArray
                  name="householdsFiltersBlocks"
                  render={(arrayHelpers) => (
                    <ArrayFieldWrapper
                      arrayHelpers={arrayHelpers}
                      ref={householdsFiltersBlocksWrapperRef}
                    >
                      {values.householdsFiltersBlocks.map((each, index) => (
                        <TargetingCriteriaHouseholdFilter
                          // eslint-disable-next-line
                          key={index}
                          index={index}
                          data={
                            isSocialWorkingProgram
                              ? data
                              : householdData.allFieldsAttributes
                          }
                          choicesDict={allDataChoicesDict}
                          each={each}
                          onChange={(e, object) => {
                            if (object) {
                              return chooseFieldType(
                                object,
                                arrayHelpers,
                                index,
                              );
                            }
                            return clearField(arrayHelpers, index);
                          }}
                          values={values}
                          onClick={() => arrayHelpers.remove(index)}
                        />
                      ))}
                    </ArrayFieldWrapper>
                  )}
                />
                {householdFiltersAvailable || isSocialWorkingProgram ? (
                  <Box display="flex" flexDirection="column">
                    <ButtonBox>
                      <Button
                        onClick={() =>
                          householdsFiltersBlocksWrapperRef.current
                            .getArrayHelpers()
                            .push({ fieldName: '' })
                        }
                        color="primary"
                        startIcon={<AddCircleOutline />}
                        data-cy="button-household-rule"
                      >
                        ADD{' '}
                        {isSocialWorkingProgram
                          ? 'PEOPLE'
                          : beneficiaryGroup?.groupLabel.toUpperCase()}{' '}
                        RULE
                      </Button>
                    </ButtonBox>
                  </Box>
                ) : null}
                {individualFiltersAvailable ? (
                  <>
                    {individualFiltersAvailable ? (
                      <AndDivider>
                        <AndDividerLabel>And</AndDividerLabel>
                      </AndDivider>
                    ) : null}
                    <Grid container spacing={3}>
                      <>
                        <Grid size={{ xs: 12 }}>
                          <Box pb={3}>
                            <Field
                              data-cy="input-included-individual-ids"
                              name="individualIds"
                              fullWidth
                              variant="outlined"
                              label={t(
                                `${beneficiaryGroup?.memberLabelPlural} IDs`,
                              )}
                              component={FormikTextField}
                            />
                          </Box>
                        </Grid>
                        <Grid size={{ xs: 12 }}>
                          <AndDivider>
                            <AndDividerLabel>AND</AndDividerLabel>
                          </AndDivider>
                        </Grid>
                      </>
                    </Grid>
                    <FieldArray
                      name="individualsFiltersBlocks"
                      render={(arrayHelpers) => (
                        <ArrayFieldWrapper
                          arrayHelpers={arrayHelpers}
                          ref={individualsFiltersBlocksWrapperRef}
                        >
                          {values.individualsFiltersBlocks.map(
                            (_each, index) => (
                              <TargetingCriteriaIndividualFilterBlocks
                                // eslint-disable-next-line
                                key={index}
                                blockIndex={index}
                                data={individualData}
                                values={values}
                                choicesToDict={allDataChoicesDict}
                                onDelete={() => arrayHelpers.remove(index)}
                              />
                            ),
                          )}
                        </ArrayFieldWrapper>
                      )}
                    />
                    <Box display="flex" flexDirection="column">
                      <ButtonBox>
                        <Button
                          data-cy="button-individual-rule"
                          onClick={() =>
                            individualsFiltersBlocksWrapperRef.current
                              .getArrayHelpers()
                              .push({
                                individualBlockFilters: [{ fieldName: '' }],
                              })
                          }
                          color="primary"
                          startIcon={<AddCircleOutline />}
                        >
                          {`ADD ${beneficiaryGroup?.memberLabel.toUpperCase()}
                          RULE GROUP`}
                        </Button>
                      </ButtonBox>
                    </Box>
                  </>
                ) : null}
                {collectorsFiltersAvailable ? (
                  <>
                    <AndDivider>
                      <AndDividerLabel>And</AndDividerLabel>
                    </AndDivider>
                    <FieldArray
                      name="collectorsFiltersBlocks"
                      render={(arrayHelpers) => (
                        <ArrayFieldWrapper
                          arrayHelpers={arrayHelpers}
                          ref={collectorsFiltersBlocksWrapperRef}
                        >
                          {values.collectorsFiltersBlocks.map(
                            (_each, index) => (
                              <TargetingCriteriaCollectorFilterBlocks
                                // eslint-disable-next-line
                                key={index}
                                blockIndex={index}
                                data={allCollectorFieldsAttributesData}
                                values={values}
                                choicesToDict={allCollectorFieldsChoicesDict}
                                onDelete={() => arrayHelpers.remove(index)}
                              />
                            ),
                          )}
                        </ArrayFieldWrapper>
                      )}
                    />
                    <Box display="flex" flexDirection="column">
                      <ButtonBox>
                        <Button
                          data-cy="button-collector-rule"
                          onClick={() =>
                            collectorsFiltersBlocksWrapperRef.current
                              .getArrayHelpers()
                              .push({
                                collectorBlockFilters: [{ fieldName: '' }],
                              })
                          }
                          color="primary"
                          startIcon={<AddCircleOutline />}
                        >
                          ADD COLLECTOR RULE GROUP
                        </Button>
                      </ButtonBox>
                    </Box>
                    {criteriaIndex === 0 && (
                      <Box mt={2} display="flex" flexDirection="column">
                        <ButtonBox style={{ width: '600px' }}>
                          <Button
                            data-cy="button-collector-rule"
                            onClick={() => handlePaymentChannelButtonClick()}
                            color="primary"
                            startIcon={<AddCircleOutline />}
                          >
                            <Box
                              style={{ textAlign: 'left' }}
                              display="flex"
                              flexDirection="column"
                            >
                              <Box>PAYMENT CHANNEL VALIDATION</Box>
                              <Box>
                                (Delivery mechanism and FSP requirements)
                              </Box>
                            </Box>
                          </Button>
                        </ButtonBox>
                        <Collapse in={openPaymentChannelCollapse}>
                          <Box mt={4}>
                            <Grid container spacing={3}>
                              <Grid size={{ xs: 12 }}>
                                <Field
                                  name="deliveryMechanism"
                                  label="Select Delivery Mechanism"
                                  type="text"
                                  fullWidth
                                  required={openPaymentChannelCollapse}
                                  variant="outlined"
                                  choices={mappedDeliveryMechanisms}
                                  component={FormikSelectField}
                                  onChange={() => {
                                    setFieldValue('fsp', '');
                                  }}
                                  onClear={() => {
                                    setFieldValue('fsp', '');
                                  }}
                                  data-cy="input-delivery-mechanism"
                                />
                              </Grid>
                              <Grid size={{ xs: 12 }}>
                                <Tooltip
                                  title={
                                    !values.deliveryMechanism
                                      ? 'Select delivery mechanism first'
                                      : ''
                                  }
                                >
                                  <div>
                                    <Field
                                      name="fsp"
                                      label="Select FSP"
                                      type="text"
                                      fullWidth
                                      disabled={!values.deliveryMechanism}
                                      required={openPaymentChannelCollapse}
                                      variant="outlined"
                                      component={FormikSelectField}
                                      choices={mappedFsps}
                                      data-cy="input-fsp"
                                    />
                                  </div>
                                </Tooltip>
                              </Grid>
                            </Grid>
                          </Box>
                        </Collapse>
                      </Box>
                    )}
                  </>
                ) : null}
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <StyledBox display="flex" justifyContent="flex-end">
                    <div>
                      <Button
                        onClick={() => {
                          resetForm();
                          onClose();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={
                          criteriaIndex === 0 &&
                          !values.deliveryMechanism &&
                          !values.fsp
                            ? () =>
                                confirm({
                                  title: t('Warning'),
                                  content: confirmationText,
                                }).then(() => {
                                  submitForm();
                                })
                            : submitForm
                        }
                        type="submit"
                        color="primary"
                        variant="contained"
                        data-cy="button-target-population-add-criteria"
                      >
                        Save
                      </Button>
                    </div>
                  </StyledBox>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          );
        }}
      </Formik>
    </DialogContainer>
  );
};
