import { Box, Button, Collapse, Grid, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { StyledTextField } from '../../../../shared/StyledTextField';
import { GreyText } from '../../../core/GreyText';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { ExcludedItem } from './ExcludedItem';

export const ExcludeSection = ({
  initialOpen = false,
}: {
  initialOpen?: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [isExclusionsOpen, setExclusionsOpen] = useState(initialOpen);
  const [value, setValue] = useState('');
  const [excludedIds, setExcludedIds] = useState<string[]>([]);
  const [deletedIds, setDeletedIds] = useState<string[]>([]);
  const [error, setError] = useState<string>('');

  const handleChange = (event): void => {
    setValue(event.target.value);
  };

  const handleSave = (): void => {
    const idsToSave = excludedIds.filter((id) => !deletedIds.includes(id));
    console.log('🤪🤪🤪 idsToSave', idsToSave);
  };

  const handleApply = (): void => {
    const idRegex = /^HH-\d{2}-\d{4}\.\d{4}$/;
    const ids = value.split(/,\s*|\s+/);
    const invalidIds: string[] = [];
    const alreadyExcludedIds: string[] = [];
    const newExcludedIds: string[] = [];

    for (const id of ids) {
      if (!idRegex.test(id)) {
        invalidIds.push(id);
      } else if (excludedIds.includes(id)) {
        alreadyExcludedIds.push(id);
      } else {
        newExcludedIds.push(id);
      }
    }

    let errorMessage = '';
    if (invalidIds.length > 0) {
      errorMessage += ` Invalid IDs: ${invalidIds.join(', ')}`;
    }
    if (alreadyExcludedIds.length > 0) {
      errorMessage += ` IDs already excluded: ${alreadyExcludedIds.join(', ')}`;
    }

    if (errorMessage) {
      setError(errorMessage.trim());
    } else {
      setError('');
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

  return (
    <PaperContainer>
      <Box display='flex' justifyContent='space-between'>
        <Typography variant='h6'>{t('Exclude')}</Typography>
        <Box display='flex' alignItems='center' justifyContent='center'>
          <Box mr={2}>
            <Button
              variant={isExclusionsOpen ? 'text' : 'contained'}
              color='primary'
              onClick={() => setExclusionsOpen(!isExclusionsOpen)}
            >
              {isExclusionsOpen ? t('Cancel') : t('Create')}
            </Button>
          </Box>
          {isExclusionsOpen && (
            <Button
              variant='contained'
              color='primary'
              onClick={() => {
                handleSave();
                setExclusionsOpen(false);
              }}
            >
              {t('Save')}
            </Button>
          )}
        </Box>
      </Box>
      <Collapse in={isExclusionsOpen}>
        <Box display='flex' flexDirection='column'>
          <Box mt={2} display='flex' alignItems='center'>
            <Grid alignItems='flex-start' container spacing={3}>
              <Grid item xs={6}>
                <Box mr={2}>
                  <StyledTextField
                    label={t('Household Ids')}
                    value={value}
                    onChange={handleChange}
                    fullWidth
                    helperText={error}
                    error={!!error}
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
          {numberOfExcluded > 0 && (
            <Box mt={2} mb={2}>
              <GreyText>{`${numberOfExcluded} ${
                numberOfExcluded === 1 ? 'Household' : 'Households'
              } excluded`}</GreyText>
            </Box>
          )}
          <Grid container item xs={4}>
            {excludedIds.map((id) => (
              <Grid item xs={12}>
                <ExcludedItem
                  key={id}
                  id={id}
                  onDelete={() => handleDelete(id)}
                  onUndo={() => handleUndo(id)}
                  isDeleted={handleCheckIfDeleted(id)}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      </Collapse>
    </PaperContainer>
  );
};
