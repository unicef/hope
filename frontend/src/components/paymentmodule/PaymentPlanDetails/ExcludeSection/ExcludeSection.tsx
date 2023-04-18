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
  const [error, setError] = useState<string>('');

  const handleChange = (event): void => {
    setValue(event.target.value);
  };

  const handleSave = (): void => {
    console.log('🤪🤪🤪', excludedIds);
  };

  const handleApply = (): void => {
    const idRegex = /^HH-\d{2}-\d{4}\.\d{4}(\s*,\s*HH-\d{2}-\d{4}\.\d{4})*$/;
    const ids = value.split(/,\s*|\s+/);
    const invalidIds = ids.filter(
      (id) => !idRegex.test(id) || excludedIds.includes(id),
    );
    const newExcludedIds = ids.filter(
      (id) => idRegex.test(id) && !excludedIds.includes(id),
    );
    if (invalidIds.length === 1) {
      setError(`Invalid ID: ${invalidIds.join(', ')}`);
    } else if (invalidIds.length > 0) {
      setError(`Invalid IDs: ${invalidIds.join(', ')}`);
    }
    if (!invalidIds.length) {
      setError('');
    }

    setExcludedIds([...excludedIds, ...newExcludedIds]);
    setValue('');
  };

  const handleDelete = (id: string): void => {
    setExcludedIds(excludedIds.filter((excludedId) => excludedId !== id));
  };

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
            <Grid alignItems='center' container spacing={3}>
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
          {excludedIds.length > 0 && (
            <Box mt={2} mb={2}>
              <GreyText>{`${excludedIds.length} ${
                excludedIds.length === 1 ? 'Household' : 'Households'
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
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      </Collapse>
    </PaperContainer>
  );
};
