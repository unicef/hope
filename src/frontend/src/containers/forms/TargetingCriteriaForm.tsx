import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Typography,
} from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { Field, FieldArray, Formik } from 'formik';
import {
  Component,
  ReactElement,
  ReactNode,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useCachedImportedIndividualFieldsQuery } from '@hooks/useCachedImportedIndividualFields';
import {
  chooseFieldType,
  clearField,
  formatCriteriaFilters,
  formatCriteriaIndividualsFiltersBlocks,
  mapCriteriaToInitialValues,
} from '@utils/targetingUtils';
import { DialogContainer } from '../dialogs/DialogContainer';
import { DialogDescription } from '../dialogs/DialogDescription';
import { DialogFooter } from '../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../dialogs/DialogTitleWrapper';
import { TargetingCriteriaIndividualFilterBlocks } from './TargetingCriteriaIndividualFilterBlocks';
import { AndDivider, AndDividerLabel } from '@components/targeting/AndDivider';
import { TargetingCriteriaHouseholdFilter } from './TargetingCriteriaHouseholdFilter';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { TargetingCriteriaCollectorFilterBlocks } from './TargetingCriteriaCollectorFilterBlocks';

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

const validationSchema = Yup.object().shape({
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
                  parent.fieldAttribute.type === 'PDU'
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
                  parent.fieldAttribute.type === 'PDU'
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
});

interface ArrayFieldWrapperProps {
  arrayHelpers;
  children: ReactNode;
}
class ArrayFieldWrapper extends Component<ArrayFieldWrapperProps> {
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
}

const associatedWith = (type) => (item) => item.associatedWith === type;
const isNot = (type) => (item) => item.type !== type;

export const TargetingCriteriaForm = ({
  criteria,
  addCriteria,
  open,
  onClose,
  individualFiltersAvailable,
  householdFiltersAvailable,
  collectorsFiltersAvailable,
  isSocialWorkingProgram,
}: TargetingCriteriaFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const { data, loading } = useCachedImportedIndividualFieldsQuery(
    businessArea,
    programId,
  );

  const filtersArrayWrapperRef = useRef(null);
  const individualsFiltersBlocksWrapperRef = useRef(null);
  const collectorsFiltersBlocksWrapperRef = useRef(null);
  const initialValue = mapCriteriaToInitialValues(criteria);
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const [allDataChoicesDict, setAllDataChoicesDict] = useState(null);
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: data?.allFieldsAttributes
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: data?.allFieldsAttributes?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
    const allDataChoicesDictTmp = data?.allFieldsAttributes?.reduce(
      (acc, item) => {
        acc[item.name] = item.choices;
        return acc;
      },
      {},
    );
    setAllDataChoicesDict(allDataChoicesDictTmp);
  }, [data, loading]);

  if (!data) return null;

  const filterNullOrNoSelections = (filter): boolean =>
    !filter.isNull &&
    (filter.value === null ||
      filter.value === '' ||
      (filter?.fieldAttribute?.type === 'SELECT_MANY' &&
        filter.value &&
        filter.value.length === 0));

  const filterEmptyFromTo = (filter): boolean =>
    !filter.isNull &&
    typeof filter.value === 'object' &&
    filter.value !== null &&
    Object.prototype.hasOwnProperty.call(filter.value, 'from') &&
    Object.prototype.hasOwnProperty.call(filter.value, 'to') &&
    !filter.value.from &&
    !filter.value.to;

  const validate = (values) => {
    const hasFiltersErrors =
      values.filters.some(filterNullOrNoSelections) ||
      values.filters.some(filterEmptyFromTo);

    const hasBlockFiltersErrors = (blocks) => {
      return blocks.some((block) => {
        const hasNulls = block.blockFilters.some(filterNullOrNoSelections);
        const hasFromToError = block.blockFilters.some(filterEmptyFromTo);
        return hasNulls || hasFromToError;
      });
    };

    const hasIndividualsFiltersBlocksErrors = hasBlockFiltersErrors(
      values.individualsFiltersBlocks,
    );
    const hasCollectorsFiltersBlocksErrors = hasBlockFiltersErrors(
      values.collectorsFiltersBlocks,
    );

    const errors: { nonFieldErrors?: string[] } = {};
    if (
      hasFiltersErrors ||
      hasIndividualsFiltersBlocksErrors ||
      hasCollectorsFiltersBlocksErrors
    ) {
      errors.nonFieldErrors = ['You need to fill out missing values.'];
    }
    if (
      values.filters.length +
        values.individualsFiltersBlocks.length +
        values.collectorsFiltersBlocks.length ===
      0
    ) {
      errors.nonFieldErrors = [
        'You need to add at least one household filter, an individual block filter, or a collector block filter.',
      ];
    } else if (
      values.individualsFiltersBlocks.filter(
        (block) => block.blockFilters.length === 0,
      ).length > 0 ||
      values.collectorsFiltersBlocks.filter(
        (block) => block.blockFilters.length === 0,
      ).length > 0
    ) {
      errors.nonFieldErrors = [
        'You need to add at least one household filter, an individual block filter, or a collector block filter.',
      ];
    }
    return errors;
  };

  const handleSubmit = (values, bag): void => {
    const filters = formatCriteriaFilters(values.filters);

    const individualsFiltersBlocks = formatCriteriaIndividualsFiltersBlocks(
      values.individualsFiltersBlocks,
    );
    addCriteria({ filters, individualsFiltersBlocks });
    return bag.resetForm();
  };
  if (loading || !open) return null;

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={handleSubmit}
        validate={validate}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values, resetForm, errors }) => {
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
                    : 'All rules defined below have to be true for the entire household.'}
                </DialogDescription>
                <Grid container spacing={3}>
                  {householdFiltersAvailable && (
                    <Grid item xs={12}>
                      <Field
                        data-cy="input-included-household-ids"
                        name="householdIds"
                        fullWidth
                        multiline
                        variant="outlined"
                        label={t('Household IDs')}
                        component={FormikTextField}
                      />
                    </Grid>
                  )}
                  {householdFiltersAvailable && individualFiltersAvailable && (
                    <Grid item xs={12}>
                      <AndDivider>
                        <AndDividerLabel>AND</AndDividerLabel>
                      </AndDivider>
                    </Grid>
                  )}
                </Grid>
                <FieldArray
                  name="filters"
                  render={(arrayHelpers) => (
                    <ArrayFieldWrapper
                      arrayHelpers={arrayHelpers}
                      ref={filtersArrayWrapperRef}
                    >
                      {values.filters.map((each, index) => (
                        <TargetingCriteriaHouseholdFilter
                          // eslint-disable-next-line
                          key={index}
                          index={index}
                          data={isSocialWorkingProgram ? data : householdData}
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
                          filtersArrayWrapperRef.current
                            .getArrayHelpers()
                            .push({ fieldName: '' })
                        }
                        color="primary"
                        startIcon={<AddCircleOutline />}
                        data-cy="button-household-rule"
                      >
                        ADD {isSocialWorkingProgram ? 'PEOPLE' : 'HOUSEHOLD'}{' '}
                        RULE
                      </Button>
                    </ButtonBox>
                  </Box>
                ) : null}
                {individualFiltersAvailable && !isSocialWorkingProgram ? (
                  <>
                    {householdFiltersAvailable ? (
                      <AndDivider>
                        <AndDividerLabel>And</AndDividerLabel>
                      </AndDivider>
                    ) : null}
                    <Grid container spacing={3}>
                      <>
                        <Grid item xs={12}>
                          <Box pb={3}>
                            <Field
                              data-cy="input-included-individual-ids"
                              name="individualIds"
                              fullWidth
                              variant="outlined"
                              label={t('Individual IDs')}
                              component={FormikTextField}
                            />
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
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
                            (each, index) => (
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
                          ADD INDIVIDUAL RULE GROUP
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
                    <Grid container spacing={3}>
                      <>
                        <Grid item xs={12}>
                          <Box pb={3}>
                            <Field
                              data-cy="input-included-collector-ids"
                              name="collectorIds"
                              fullWidth
                              variant="outlined"
                              label={t('Collector IDs')}
                              component={FormikTextField}
                            />
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
                          <AndDivider>
                            <AndDividerLabel>AND</AndDividerLabel>
                          </AndDivider>
                        </Grid>
                      </>
                    </Grid>
                    <FieldArray
                      name="collectorsFiltersBlocks"
                      render={(arrayHelpers) => (
                        <ArrayFieldWrapper
                          arrayHelpers={arrayHelpers}
                          ref={collectorsFiltersBlocksWrapperRef}
                        >
                          {values.collectorsFiltersBlocks.map((each, index) => (
                            <TargetingCriteriaCollectorFilterBlocks
                              // eslint-disable-next-line
                              key={index}
                              blockIndex={index}
                              data={individualData}
                              values={values}
                              choicesToDict={allDataChoicesDict}
                              onDelete={() => arrayHelpers.remove(index)}
                            />
                          ))}
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
                        onClick={submitForm}
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
