import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useGrievanceTicketLazyQuery } from '@generated/graphql';
import { usePermissions } from '@hooks/usePermissions';
import PersonIcon from '@mui/icons-material/Person';
import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@mui/material';
import { FC, ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

export interface Individual {
  __typename?: 'DeduplicationEngineSimilarityPairIndividualNode';
  unicefId?: string;
  fullName?: string;
  photo?: string;
}

export interface BiometricsResultsProps {
  ticketId: string;
  similarityScore: string;
  individual1?: Individual;
  individual2?: Individual;
  statusCode?: string;
}

const Placeholder: FC = () => (
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
  ticketId,
  similarityScore,
  individual1,
  individual2,
  statusCode,
}: BiometricsResultsProps): ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const permissions = usePermissions();
  const canViewBiometricsResults = hasPermissions(
    PERMISSIONS.GRIEVANCES_VIEW_BIOMETRIC_RESULTS,
    permissions,
  );
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const [loadData] = useGrievanceTicketLazyQuery({
    variables: {
      id: ticketId,
    },
    fetchPolicy: 'cache-and-network',
  });

  return (
    <>
      {canViewBiometricsResults && (
        <Box p={2}>
          <Button
            onClick={() => {
              setDialogOpen(true);
              loadData();
            }}
            data-cy="button-open-biometrics-results"
          >
            {t('View Biometrics Results')}
          </Button>
        </Box>
      )}
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
              {individual1?.unicefId && (
                <Box display="flex" flexDirection="column">
                  {individual1?.photo ? (
                    <img
                      src={individual1?.photo}
                      alt="Image 1"
                      style={{
                        maxWidth: '100%',
                        maxHeight: '300px',
                        objectFit: 'cover',
                      }}
                      data-cy="image1"
                    />
                  ) : (
                    <Placeholder />
                  )}
                  <Typography variant="subtitle2">
                    {beneficiaryGroup?.memberLabel} {individual1?.unicefId}:{' '}
                    {individual1?.fullName}
                  </Typography>
                </Box>
              )}

              {individual2?.unicefId && (
                <Box display="flex" flexDirection="column">
                  {individual2?.photo ? (
                    <img
                      src={individual2?.photo}
                      alt="Image 2"
                      style={{
                        maxWidth: '100%',
                        maxHeight: '300px',
                        objectFit: 'cover',
                      }}
                      data-cy="image2"
                    />
                  ) : (
                    <Placeholder />
                  )}
                  <Typography variant="subtitle2">
                    {beneficiaryGroup?.memberLabel} {individual2?.unicefId}:{' '}
                    {individual2?.fullName}
                  </Typography>
                </Box>
              )}

              {individual2?.unicefId && (
                <Box display="flex" flexDirection="column">
                  {individual2?.photo ? (
                    <img
                      src={individual2?.photo}
                      alt="Image 2"
                      style={{
                        maxWidth: '100%',
                        maxHeight: '300px',
                        objectFit: 'cover',
                      }}
                      data-cy="image2"
                    />
                  ) : (
                    <Placeholder />
                  )}
                  <Typography variant="subtitle2">
                    {beneficiaryGroup?.memberLabel} {individual2?.unicefId}:{' '}
                    {individual2?.fullName}
                  </Typography>
                </Box>
              )}
            </Box>
            <Box p={5} data-cy="results-info">
              <div>
                <strong>
                  {t('Algorithm similarity score:')} {similarityScore}
                </strong>
              </div>
              {Number(similarityScore) > 0 ? (
                <div>{t('Face images matching suggests: Duplicates')}</div>
              ) : (
                statusCode
              )}
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
