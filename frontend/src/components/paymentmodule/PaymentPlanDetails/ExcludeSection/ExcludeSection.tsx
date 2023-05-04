import {
  Box,
  Button,
  Collapse,
  FormHelperText,
  Grid,
  Typography,
} from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  PaymentPlanDocument,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useExcludeHouseholdsPpMutation,
} from '../../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
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
  const permissions = usePermissions();
  const canEditExclude = paymentPlan.status === PaymentPlanStatus.Locked;
  const initialExcludedIds = paymentPlan?.excludedHouseholds?.map(
    (el) => el.unicefId,
  );
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [isExclusionsOpen, setExclusionsOpen] = useState(initialOpen);
  const [value, setValue] = useState('');
  const [excludedIds, setExcludedIds] = useState<string[]>(
    initialExcludedIds || [],
  );
  const [deletedIds, setDeletedIds] = useState<string[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isEdit, setEdit] = useState(false);

  const [mutate, { error }] = useExcludeHouseholdsPpMutation();

  const handleChange = (event): void => {
    if (event.target.value === '') {
      setErrors([]);
    }
    setValue(event.target.value);
  };

  const handleSave = async (): Promise<void> => {
    const idsToSave = excludedIds.filter((id) => !deletedIds.includes(id));
    try {
      await mutate({
        variables: {
          paymentPlanId: paymentPlan.id,
          excludedHouseholdsIds: idsToSave,
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
        showMessage(t('Households excluded from Payment Plan'));
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleApply = (): void => {
    const idRegex = /^(\s*HH-\d{2}-\d{4}\.\d{4}\s*)(,\s*HH-\d{2}-\d{4}\.\d{4}\s*)*$/;
    const ids = value.trim().split(/,\s*|\s+/);
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
      setValue('');
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
  const canExclude = hasPermissions(
    PERMISSIONS.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP,
    permissions,
  );

  const renderButtons = (): React.ReactElement => {
    const noExclusions = numberOfExcluded === 0;
    const editMode = isExclusionsOpen && isEdit;
    const previewMode = !isExclusionsOpen && numberOfExcluded > 0;
    const editAllowed = isExclusionsOpen && !isEdit && canEditExclude;

    const resetExclusions = (): void => {
      setExclusionsOpen(false);
      setErrors([]);
      setExcludedIds([]);
      setDeletedIds([]);
      setValue('');
      setEdit(false);
    };

    const closeExclusions = (): void => {
      setExclusionsOpen(false);
    };

    const saveExclusions = (): void => {
      handleSave();
      setExclusionsOpen(false);
    };

    if (editMode) {
      return (
        <Box display='flex' alignItems='center' justifyContent='center'>
          <Box mr={2}>
            <Button variant='text' color='primary' onClick={resetExclusions}>
              {t('Cancel')}
            </Button>
          </Box>
          <ButtonTooltip
            variant='contained'
            color='primary'
            disabled={!canExclude || excludedIds.length === 0}
            onClick={saveExclusions}
          >
            {t('Save')}
          </ButtonTooltip>
        </Box>
      );
    }

    if (editAllowed) {
      return (
        <Button
          color='primary'
          variant='outlined'
          startIcon={<EditIcon />}
          onClick={() => setEdit(true)}
        >
          {t('Edit')}
        </Button>
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
        <Button color='primary' onClick={closeExclusions}>
          {t('Close')}
        </Button>
      );
    }

    if (noExclusions) {
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
    if (isEdit || numberOfExcluded === 0) {
      return (
        <Box mt={2} display='flex' alignItems='center'>
          <Grid alignItems='flex-start' container spacing={3}>
            <Grid item xs={6}>
              <Box mr={2}>
                <StyledTextField
                  label={t('Household Ids')}
                  value={value}
                  onChange={handleChange}
                  fullWidth
                  error={errors.length > 0}
                />
              </Box>
            </Grid>
            <Grid item>
              <Button
                variant='contained'
                color='primary'
                disabled={!value}
                onClick={() => {
                  handleApply();
                }}
              >
                {t('Apply')}
              </Button>
            </Grid>
          </Grid>
        </Box>
      );
    }
    return null;
  };

  return (
    <PaperContainer>
      <Box display='flex' justifyContent='space-between'>
        <Typography variant='h6'>{t('Exclude')}</Typography>
        {renderButtons()}
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
        </Box>
      </Collapse>
    </PaperContainer>
  );
};
