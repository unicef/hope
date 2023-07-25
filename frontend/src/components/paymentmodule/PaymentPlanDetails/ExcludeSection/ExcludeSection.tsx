import {
  Box,
  Button,
  Collapse,
  FormHelperText,
  Grid,
  Typography,
} from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import { Field, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  PaymentPlanDocument,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useExcludeHouseholdsPpMutation,
} from '../../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { StyledTextField } from '../../../../shared/StyledTextField';
import { ButtonTooltip } from '../../../core/ButtonTooltip';
import { GreyText } from '../../../core/GreyText';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { ExcludedItem } from './ExcludedItem';

interface ExcludeSectionProps {
  initialOpen?: boolean;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const ExcludeSection = ({
  initialOpen = false,
  paymentPlan,
}: ExcludeSectionProps): React.ReactElement => {
  const { status, exclusionReason, excludeHouseholdError } = paymentPlan;

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
  const hasExcludePermission = hasPermissions(
    PERMISSIONS.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP,
    permissions,
  );
  const hasOpenOrLockedStatus =
    status === PaymentPlanStatus.Locked || status === PaymentPlanStatus.Open;

  const getTooltipText = (): string => {
    if (!hasOpenOrLockedStatus) {
      return t(
        'Households can only be excluded from a Payment Plan in status open or locked',
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
    exclusionReason: '',
  };
  const validationSchema = Yup.object().shape({
    exclusionReason: Yup.string()
      .max(500, t('Too long'))
      .required(t('Exclusion reason is required')),
  });

  const handleSave = async (values): Promise<void> => {
    const idsToSave = excludedIds.filter((id) => !deletedIds.includes(id));
    try {
      await mutate({
        variables: {
          paymentPlanId: paymentPlan.id,
          excludedHouseholdsIds: idsToSave,
          exclusionReason: values.exclusionReason,
        },
        refetchQueries: () => [
          {
            query: PaymentPlanDocument,
            variables: { id: paymentPlan.id },
            fetchPolicy: 'network-only',
          },
          'AllPaymentsForTable',
        ],
      });
      if (!error) {
        showMessage(t('Households exclusion started'));
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleApply = (): void => {
    const idRegex = /^(\s*HH-\d{2}-\d{4}\.\d{4}\s*)(,\s*HH-\d{2}-\d{4}\.\d{4}\s*)*$/;
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

  const handleCheckIfDeleted = (id: string): boolean => {
    return deletedIds.includes(id);
  };

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
      !values.exclusionReason;

    const editExclusionsDisabled =
      !hasExcludePermission || !hasOpenOrLockedStatus;

    if (editMode) {
      return (
        <Box display='flex' alignItems='center' justifyContent='center'>
          <Box mr={2}>
            <Button variant='text' color='primary' onClick={resetExclusions}>
              {t('Cancel')}
            </Button>
          </Box>
          <ButtonTooltip
            title={getTooltipText()}
            variant='contained'
            color='primary'
            disabled={saveExclusionsDisabled}
            onClick={saveExclusions}
          >
            {t('Save')}
          </ButtonTooltip>
        </Box>
      );
    }

    if (previewMode) {
      return (
        <Button
          variant='contained'
          color='primary'
          onClick={() => {
            setExclusionsOpen(true);
            setEdit(false);
          }}
        >
          {t('Preview')}
        </Button>
      );
    }

    if (isExclusionsOpen) {
      return (
        <Box display='flex' alignItems='center' justifyContent='center'>
          <Box mr={2}>
            <Button variant='text' color='primary' onClick={resetExclusions}>
              {t('Close')}
            </Button>
          </Box>
          {hasExcludePermission && (
            <ButtonTooltip
              color='primary'
              title={getTooltipText()}
              disabled={editExclusionsDisabled}
              variant='outlined'
              startIcon={<EditIcon />}
              onClick={() => setEdit(true)}
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
          variant='contained'
          color='primary'
          onClick={() => {
            setExclusionsOpen(true);
            setEdit(true);
          }}
        >
          {t('Create')}
        </Button>
      );
    }

    return null;
  };

  const renderInputAndApply = (): React.ReactElement => {
    const applyDisabled = !hasExcludePermission || !hasOpenOrLockedStatus;

    if (isEdit || numberOfExcluded === 0) {
      return (
        <Box mt={2} display='flex' alignItems='center'>
          <Grid alignItems='flex-start' container spacing={3}>
            <Grid item xs={6}>
              <Box mr={2}>
                <StyledTextField
                  label={t('Household Ids')}
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
                variant='contained'
                color='primary'
                disabled={!idsValue || applyDisabled}
                onClick={() => {
                  handleApply();
                }}
              >
                {t('Apply')}
              </ButtonTooltip>
            </Grid>
            <Grid item xs={12}>
              <Field
                name='exclusionReason'
                fullWidth
                multiline
                variant='outlined'
                label={t('Exclusion Reason')}
                component={FormikTextField}
              />
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
    >
      {({ submitForm, values, resetForm }) => {
        return (
          <Form>
            <PaperContainer>
              <Box display='flex' justifyContent='space-between'>
                <Typography variant='h6'>{t('Exclude')}</Typography>
                {renderButtons(submitForm, values, resetForm)}
              </Box>
              {!isExclusionsOpen && numberOfExcluded > 0 ? (
                <Box mt={2} mb={2}>
                  <GreyText>{`${numberOfExcluded} ${
                    numberOfExcluded === 1 ? 'Household' : 'Households'
                  } excluded`}</GreyText>
                </Box>
              ) : null}
              <Collapse in={isExclusionsOpen}>
                <Box display='flex' flexDirection='column'>
                  {renderInputAndApply()}
                  <Grid container item xs={6}>
                    {errors?.map((formError) => (
                      <Grid item xs={12}>
                        <FormHelperText error>{formError}</FormHelperText>
                      </Grid>
                    ))}
                  </Grid>
                  {numberOfExcluded > 0 && (
                    <Box mt={2} mb={2}>
                      <GreyText>{`${numberOfExcluded} ${
                        numberOfExcluded === 1 ? 'Household' : 'Households'
                      } excluded`}</GreyText>
                    </Box>
                  )}
                  <Grid container direction='column' item xs={3}>
                    {excludedIds.map((id) => (
                      <Grid item xs={12}>
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
                  {isExclusionsOpen && exclusionReason ? (
                    <Grid container>
                      <Grid item xs={8}>
                        <Box display='flex' flexDirection='column'>
                          <Box mt={4} mb={2}>
                            <Typography variant='subtitle2'>
                              {t('Exclusion Reason')}:
                            </Typography>
                          </Box>
                          <Box>
                            <Typography>{exclusionReason}</Typography>
                          </Box>
                          {excludeHouseholdError && (
                            <Box display='flex' flexDirection='column' mt={2}>
                              {formatErrorToArray(excludeHouseholdError).map(
                                (el) => (
                                  <FormHelperText error>{el}</FormHelperText>
                                ),
                              )}
                            </Box>
                          )}
                        </Box>
                      </Grid>
                    </Grid>
                  ) : null}
                </Box>
              </Collapse>
            </PaperContainer>
          </Form>
        );
      }}
    </Formik>
  );
};
