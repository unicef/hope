import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import PersonIcon from '@mui/icons-material/Person';
import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export interface BiometricsResultsProps {
  similarityScore: number;
  faceMatchResult: 'Duplicates' | 'Uniqueness';
  image1?: string;
  image2?: string;
}

const Placeholder: React.FC = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    width="45%"
    height="200px"
    border="1px solid #ccc"
    data-cy="placeholder"
  >
    <PersonIcon color="primary" style={{ fontSize: 100 }} />
  </Box>
);

export const BiometricsResults = ({
  similarityScore,
  faceMatchResult,
  image1,
  image2,
}: BiometricsResultsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <Box p={2}>
        <Button
          onClick={() => setDialogOpen(true)}
          data-cy="button-open-biometrics-results"
        >
          {t('Open Biometrics Results')}
        </Button>
      </Box>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
        data-cy="dialog-biometrics-results"
      >
        <DialogTitleWrapper>
          <DialogTitle data-cy="dialog-title">
            {t('Biometrics Results')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent data-cy="dialog-content">
          <DialogContainer>
            <Box display="flex" justifyContent="space-between" p={5}>
              {image1 ? (
                <img
                  src={image1}
                  alt="Image 1"
                  style={{ width: '45%' }}
                  data-cy="image1"
                />
              ) : (
                <Placeholder />
              )}
              {image2 ? (
                <img
                  src={image2}
                  alt="Image 2"
                  style={{ width: '45%' }}
                  data-cy="image2"
                />
              ) : (
                <Placeholder />
              )}
            </Box>
            <Box p={5} data-cy="results-info">
              <div>
                <strong>
                  {t('Algorithm similarity score:')} {similarityScore}
                </strong>
              </div>
              <div>
                {t('Face images matching suggests:')} {faceMatchResult}
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} data-cy="button-close">
              {t('CLOSE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
