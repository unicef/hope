import withErrorBoundary from '@components/core/withErrorBoundary';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { usePermissions } from '@hooks/usePermissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import PersonIcon from '@mui/icons-material/Person';
import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@mui/material';
import { FC, ReactElement, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

export interface BiometricsResultsProps {
  similarityScore: number;
  individual1?: any;
  individual2?: any;
  openLinkText?: string;
  modalTitle?: string;
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

const BiometricsResultsRdi = ({
  similarityScore,
  individual1,
  individual2,
  openLinkText = 'View Similarity Details',
  modalTitle = 'Biometrics Results',
}: BiometricsResultsProps): ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const permissions = usePermissions();
  const [individual1Data, setIndividual1Data] = useState<any>(individual1);
  const [individual2Data, setIndividual2Data] = useState<any>(individual2);

  const canViewBiometricsResults = hasPermissions(
    PERMISSIONS.GRIEVANCES_VIEW_BIOMETRIC_RESULTS,
    permissions,
  );

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { businessAreaSlug, programSlug } = useBaseUrl();

  const individual1Query = useQuery({
    queryKey: ['individual', individual1?.id, businessAreaSlug, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug,
        id: individual1?.id,
        programSlug,
      }),
    enabled: dialogOpen && !!individual1?.id,
  });

  const individual2Query = useQuery({
    queryKey: ['individual', individual2?.id, businessAreaSlug, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug,
        id: individual2?.id,
        programSlug,
      }),
    enabled: dialogOpen && !!individual2?.id,
  });

  useEffect(() => {
    if (individual1Query.data) {
      setIndividual1Data(individual1Query.data);
    }
  }, [individual1Query.data]);

  useEffect(() => {
    if (individual2Query.data) {
      setIndividual2Data(individual2Query.data);
    }
  }, [individual2Query.data]);

  return (
    <>
      <Box p={2}>
        {canViewBiometricsResults && (
          <Button
            onClick={(e) => {
              e.stopPropagation();
              setDialogOpen(true);
            }}
            data-cy="button-open-biometrics-results"
          >
            {t(openLinkText)}
          </Button>
        )}
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
          <DialogTitle data-cy="dialog-title">{t(modalTitle)}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent data-cy="dialog-content">
          <DialogContainer>
            <Box display="flex" justifyContent="space-between" p={5}>
              <Box display="flex" flexDirection="column">
                {individual1Data?.photo ? (
                  <img
                    src={individual1Data?.photo}
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
                  {beneficiaryGroup?.memberLabel} {individual1Data?.unicefId}:{' '}
                  {individual1Data?.fullName}
                </Typography>
              </Box>
              <Box display="flex" flexDirection="column">
                {individual2Data?.photo ? (
                  <img
                    src={individual2Data?.photo}
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
                  {beneficiaryGroup?.memberLabel} {individual2Data?.unicefId}:{' '}
                  {individual2Data?.fullName}
                </Typography>
              </Box>
            </Box>
            <Box p={5} data-cy="results-info">
              <div>
                <strong>
                  {t('Algorithm similarity score:')} {similarityScore}
                </strong>
              </div>
              <div>{t('Face images matching suggests: Duplicates')}</div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                setDialogOpen(false);
              }}
              data-cy="button-close"
            >
              {t('CLOSE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};

export default withErrorBoundary(BiometricsResultsRdi, 'BiometricsResultsRdi');
