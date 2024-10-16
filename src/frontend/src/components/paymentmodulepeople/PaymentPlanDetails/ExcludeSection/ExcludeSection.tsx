import {
  Box,
  Button,
  Collapse,
  FormHelperText,
  Grid,
  Typography,
} from '@mui/material';
import { Field, Form, Formik } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  PaymentPlanDocument,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useExcludeHouseholdsPpMutation,
} from '@generated/graphql';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { StyledTextField } from '@shared/StyledTextField';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { GreyText } from '@core/GreyText';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { useProgramContext } from '../../../../programContext';
import { ExcludedItem } from './ExcludedItem';

interface ExcludeSectionProps {
  initialOpen?: boolean;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function ExcludeSection({
  initialOpen = false,
  paymentPlan,
}: ExcludeSectionProps): React.ReactElement {
  const {
    status,
    backgroundActionStatus,
    exclusionReason,
    excludeHouseholdError,
  } = paymentPlan;

  const initialExcludedIds = paymentPlan?.excludedHouseholds?.map(
    (el) => el.unicefId,
  );
  const [isExclusionsOpen, setExclusionsOpen] = useState(initialOpen);
  const [idsValue, setIdsValue] = useState('');
  const [excludedIds, setExcludedIds] = useState<string[]>(
    initialExcludedIds || [],
  );
  const [deletedIds, setDeletedIds] = useState<string[]>([]);
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { isActiveProgram } = useProgramContext();

  const hasExcludePermission = hasPermissions(
    PERMISSIONS.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP,
    permissions,
  );
  const hasOpenOrLockedStatus =
    status === PaymentPlanStatus.Locked || status === PaymentPlanStatus.Open;

  const getTooltipText = (): string => {
    if (!hasOpenOrLockedStatus) {
      return t(
        'Beneficiaries can only be excluded from a Payment Plan in status open or locked',
      );
    }
    if (!hasExcludePermission) {
      return t('Permission denied');
    }
    return '';
  };

  const { showMessage } = useSnackbar();
  const [errors, setErrors] = useState<string[]>([]);
  const [isEdit, setEdit] = useState(false);

  const [mutate, { error }] = useExcludeHouseholdsPpMutation();

  const handleIdsChange = (event): void => {
    if (event.target.value === '') {
      setErrors([]);
    }
    setIdsValue(event.target.value);
  };
  const initialValues = {
    exclusionReason: paymentPlan.exclusionReason || '',
  };
  const validationSchema = Yup.object().shape({
    exclusionReason: Yup.string().max(500, t('Too long')),
  });

  const handleSave = async (values): Promise<void> => {
    const idsToSave = excludedIds.filter((id) => !deletedIds.includes(id));
    try {
      await mutate({
        variables: {
          paymentPlanId: paymentPlan.id,
          excludedHouseholdsIds: idsToSave,
          exclusionReason: values.exclusionReason || null,
        },
        refetchQueries: () => [
          {
            query: PaymentPlanDocument,
            variables: { id: paymentPlan.id },
            fetchPolicy: 'network-only',
          },
          'AllPaymentsForTable',
        ],
        awaitRefetchQueries: true,
      });
      if (!error) {
        showMessage(t('Beneficiaries exclusion started'));
        setExclusionsOpen(false);
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleApply = (): void => {
    const idRegex =
      /^(\s*IND-\d{2}-\d{4}\.\d{4}\s*)(,\s*IND-\d{2}-\d{4}\.\d{4}\s*)*$/;
    const ids = idsValue.trim().split(/,\s*|\s+/);
    const invalidIds: string[] = [];
    const alreadyExcludedIds: string[] = [];
    const newExcludedIds: string[] = [];

    for (const id of ids) {
      if (!idRegex.test(id)) {
        invalidIds.push(id);
      } else if (excludedIds.includes(id.trim())) {
        alreadyExcludedIds.push(id);
      } else {
        newExcludedIds.push(id);
      }
    }

    const idErrors: string[] = [];
    if (invalidIds.length > 0) {
      idErrors.push(` Invalid IDs: ${invalidIds.join(', ')}`);
    }
    if (alreadyExcludedIds.length > 0) {
      idErrors.push(` IDs already excluded: ${alreadyExcludedIds.join(', ')}`);
    }

    if (idErrors.length > 0) {
      setErrors(idErrors);
    } else {
      setErrors([]);
      setExcludedIds([...excludedIds, ...newExcludedIds]);
      setIdsValue('');
    }
  };

  const handleDelete = (id: string): void => {
    if (!deletedIds.includes(id)) {
      setDeletedIds([...deletedIds, id]);
    }
  };

  const handleUndo = (id: string): void => {
    if (deletedIds.includes(id)) {
      setDeletedIds(deletedIds.filter((deletedId) => deletedId !== id));
    }
  };

  const handleCheckIfDeleted = (id: string): boolean => deletedIds.includes(id);

  const numberOfExcluded = excludedIds.length - deletedIds.length;

  const renderButtons = (submitForm, values, resetForm): React.ReactElement => {
    const noExclusions = numberOfExcluded === 0;
    const editMode = isExclusionsOpen && isEdit;
    const previewMode =
      (!isExclusionsOpen && numberOfExcluded > 0) ||
      (!isExclusionsOpen && deletedIds.length > 0);

    const resetExclusions = (): void => {
      setExclusionsOpen(false);
      setErrors([]);
      setIdsValue('');
      resetForm();
      setEdit(false);
    };

    const saveExclusions = (): void => {
      submitForm();
    };
    const saveExclusionsDisabled =
      !hasExcludePermission ||
      !hasOpenOrLockedStatus ||
      excludedIds.length === 0 ||
      Boolean(backgroundActionStatus);

    const editExclusionsDisabled =
      !hasExcludePermission || !hasOpenOrLockedStatus;

    if (editMode) {
      return (
        <Box display="flex" alignItems="center" justifyContent="center">
          <Box mr={2}>
            <Button
              variant="text"
              color="primary"
              data-cy="button-cancel-exclusions"
              onClick={resetExclusions}
            >
              {t('Cancel')}
            </Button>
          </Box>
          <ButtonTooltip
            title={getTooltipText()}
            variant="contained"
            color="primary"
            disabled={saveExclusionsDisabled}
            onClick={saveExclusions}
            data-cy="button-save-exclusions"
          >
            {t('Save')}
          </ButtonTooltip>
        </Box>
      );
    }

    if (previewMode) {
      return (
        <Button
          variant="contained"
          color="primary"
          onClick={() => {
            setExclusionsOpen(true);
            setEdit(false);
          }}
          data-cy="button-preview-exclusions"
        >
          {t('Preview Exclusion')}
        </Button>
      );
    }

    if (isExclusionsOpen) {
      return (
        <Box display="flex" alignItems="center" justifyContent="center">
          <Box mr={2}>
            <Button variant="text" color="primary" onClick={resetExclusions}>
              {t('Close')}
            </Button>
          </Box>
          {hasExcludePermission && (
            <ButtonTooltip
              color="primary"
              title={getTooltipText()}
              disabled={editExclusionsDisabled}
              variant="contained"
              onClick={() => setEdit(true)}
              data-cy="button-edit-exclusions"
            >
              {t('Edit')}
            </ButtonTooltip>
          )}
        </Box>
      );
    }

    if (noExclusions && !deletedIds.length) {
      return (
        <Button
          variant="contained"
          color="primary"
          data-cy="button-create-exclusions"
          onClick={() => {
            setExclusionsOpen(true);
            setEdit(true);
          }}
          disabled={!isActiveProgram}
        >
          {t('Create')}
        </Button>
      );
    }

    return null;
  };

  const renderInputAndApply = (): React.ReactElement => {
    const applyDisabled =
      !hasExcludePermission ||
      !hasOpenOrLockedStatus ||
      Boolean(backgroundActionStatus);

    if (isEdit || numberOfExcluded === 0) {
      return (
        <Box mt={2} display="flex" alignItems="center">
          <Grid alignItems="flex-start" container spacing={3}>
            <Grid item xs={12}>
              <Field
                name="exclusionReason"
                fullWidth
                multiline
                variant="outlined"
                label={t('Reason')}
                component={FormikTextField}
              />
            </Grid>
            <Grid item xs={6}>
              <Box mr={2}>
                <StyledTextField
                  label={t('Beneficiaries Ids')}
                  data-cy="input-beneficiaries-ids"
                  value={idsValue}
                  onChange={handleIdsChange}
                  fullWidth
                  error={errors.length > 0}
                />
              </Box>
            </Grid>
            <Grid item>
              <ButtonTooltip
                title={getTooltipText()}
                variant="contained"
                color="primary"
                disabled={!idsValue || applyDisabled}
                data-cy="button-apply-exclusions"
                onClick={() => {
                  handleApply();
                }}
              >
                {t('Apply')}
              </ButtonTooltip>
            </Grid>
          </Grid>
        </Box>
      );
    }
    return null;
  };

  const formatErrorToArray = (errorsString): string[] => {
    // Remove brackets and quotes
    const formattedError = errorsString.replace(/\[|\]|'|"/g, '');

    // Split the formatted error into an array of strings
    const errorArray = formattedError.split(', ');

    return errorArray;
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={(values) => handleSave(values)}
      enableReinitialize
    >
      {({ submitForm, values, resetForm }) => (
        <Form>
          <PaperContainer>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="h6">{t('Exclude')}</Typography>
              {renderButtons(submitForm, values, resetForm)}
            </Box>
            {!isExclusionsOpen && numberOfExcluded > 0 ? (
              <Box mt={2} mb={2}>
                <GreyText>
                  {`${numberOfExcluded} ${
                    numberOfExcluded === 1 ? 'Beneficiary' : 'Beneficiaries'
                  } excluded`}
                </GreyText>
              </Box>
            ) : null}
            <Collapse in={isExclusionsOpen}>
              <Box display="flex" flexDirection="column">
                {isExclusionsOpen && exclusionReason && !isEdit ? (
                  <Grid container>
                    <Grid item xs={8}>
                      <Box display="flex" flexDirection="column">
                        <Box
                          display="flex"
                          alignItems={
                            exclusionReason.length > 100
                              ? 'flex-start'
                              : 'center'
                          }
                          mt={4}
                          mb={2}
                        >
                          <Box mr={2}>
                            <GreyText>{t('Reason')}:</GreyText>
                          </Box>
                          <Typography>{exclusionReason}</Typography>
                        </Box>
                        {excludeHouseholdError && (
                          <Box display="flex" flexDirection="column" mt={2}>
                            {formatErrorToArray(excludeHouseholdError).map(
                              (el) => (
                                <FormHelperText key={el} error>
                                  {el}
                                </FormHelperText>
                              ),
                            )}
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  </Grid>
                ) : null}
                {renderInputAndApply()}
                <Grid container item xs={6}>
                  {errors?.map((formError) => (
                    <Grid key={formError} item xs={12}>
                      <FormHelperText key={formError} error>
                        {formError}
                      </FormHelperText>
                    </Grid>
                  ))}
                </Grid>
                <Grid container direction="column" item xs={3}>
                  {excludedIds.map((id) => (
                    <Grid key={id} item xs={12}>
                      <ExcludedItem
                        key={id}
                        id={id}
                        onDelete={() => handleDelete(id)}
                        onUndo={() => handleUndo(id)}
                        isDeleted={handleCheckIfDeleted(id)}
                        isEdit={isEdit}
                      />
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </Collapse>
          </PaperContainer>
        </Form>
      )}
    </Formik>
  );
}
