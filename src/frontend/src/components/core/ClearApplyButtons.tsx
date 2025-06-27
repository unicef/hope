import { Box, Button, Grid2 as Grid } from '@mui/material';
import { ReactElement, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface ClearApplyButtonsProps {
  clearHandler: () => void;
  applyHandler: () => void;
}

export function ClearApplyButtons({
  clearHandler,
  applyHandler,
}: ClearApplyButtonsProps): ReactElement {
  const { t } = useTranslation();

  const handleKeyPress = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        applyHandler();
      }
    },
    [applyHandler],
  );

  useEffect(() => {
    const handleDocumentKeyPress = (event: KeyboardEvent): void => {
      handleKeyPress(event);
    };

    document.addEventListener('keydown', handleDocumentKeyPress);
    return () => {
      document.removeEventListener('keydown', handleDocumentKeyPress);
    };
  }, [handleKeyPress]);

  return (
    <Grid container justifyContent="flex-end" spacing={3}>
      <Box mt={6}>
        <Button
          color="primary"
          data-cy="button-filters-clear"
          onClick={clearHandler}
        >
          {t('Clear')}
        </Button>
        <Button
          color="primary"
          variant="outlined"
          data-cy="button-filters-apply"
          onClick={applyHandler}
        >
          {t('Apply')}
        </Button>
      </Box>
    </Grid>
  );
}
